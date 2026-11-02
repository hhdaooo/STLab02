"""CSV-driven execution, requirement traceability and Excel/HTML reporting."""
from pathlib import Path
import csv, datetime, html, json
from collections import Counter
import pandas as pd
from ecommerce_app import fixture

ROOT = Path(__file__).resolve().parent if '__file__' in globals() else Path('.').resolve()

def execute_case(row):
    app, user, cart = fixture(row['fixture_key'])
    inp = json.loads(row['input_json']) if row.get('input_json') else {}
    op = inp.get('op')

    actual_error = ''; actual = ''; order = None
    before = {k: p.stock for k, p in app.catalog.products.items()}

    try:
        if op == 'cart_add':
            cart.add('A', int(inp.get('qty')))
            actual = 'SUCCESS'
        elif op == 'cart_add_dup':
            cart.add('A', int(inp.get('qty'))); cart.add('A', int(inp.get('qty')))
            actual = str(cart.lines[0].quantity)
        elif op == 'check_shipping':
            actual = str(app.shipping.calculate(cart.subtotal(), inp.get('area')))
        elif op == 'place_order':
            order = app.place(user, cart, method=inp.get('method'), approved=inp.get('approved'), key=row['test_case_id'])
            actual = order.status
        elif op == 'place_order_stock':
            app.place(user, cart, method=inp.get('method'), approved=inp.get('approved'), key=row['test_case_id'])
            actual = 'SUCCESS'
        else: raise ValueError('UNKNOWN_TEST_OPERATION')
    except ValueError as exc:
        actual_error = str(exc)
        actual = f'ERROR:{actual_error}'

    after = {k: p.stock for k, p in app.catalog.products.items()}
    expectation = row['expected_json']
    expected_type = row['expected_type']

    if expected_type == 'equals':
        passed = (actual == expectation)
    elif expected_type == 'stock_unchanged':
        actual_status = 'UNCHANGED' if before == after else 'CHANGED'
        passed = (actual == expectation) and (actual_status == 'UNCHANGED')
        actual = f'Stock: {actual_status} | {actual}'
    else:
        raise ValueError('UNKNOWN_ASSERTION')
    return {
        **row,
        'actual_result': actual,
        'error_message': actual_error,
        'execution_status': 'PASS' if passed else 'FAIL',
        'observed_before': json.dumps(before),
        'observed_after': json.dumps(after),
        'executed_at': datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

def run_suite(csv_path=None, out_dir=None):
    csv_path = Path(csv_path or ROOT / 'STLab02_Ecommerce_TestCases.csv')
    output = Path(out_dir or ROOT / 'reports'); output.mkdir(exist_ok=True, parents=True)

    with csv_path.open(newline='', encoding='utf-8-sig') as f:
        testcases = list(csv.DictReader(f))

    ids = [x['test_case_id'] for x in testcases]
    if len(ids) != len(set(ids)): raise ValueError('DUPLICATE_TEST_IDS')

    results = [execute_case(x) for x in testcases]
    df = pd.DataFrame(results)
    summary = df.groupby(['requirement_id', 'execution_status']).size().unstack(fill_value=0).reset_index()
    counts = Counter(df.execution_status)
    totals = pd.DataFrame([{'executed': len(df), 'passed': counts['PASS'], 'failed': counts['FAIL'], 'pass_rate': round(100 * counts['PASS'] / len(df), 1) if len(df) > 0 else 0}])

    df.to_csv(output / 'test_execution.csv', index=False, encoding='utf-8-sig')

    with pd.ExcelWriter(output / 'test_report.xlsx', engine='openpyxl') as xls:
        df.to_excel(xls, index=False, sheet_name='Execution')
        summary.to_excel(xls, index=False, sheet_name='Traceability')
        totals.to_excel(xls, index=False, sheet_name='Summary')

    rows = ''.join('<tr>' + ''.join(f'<td>{html.escape(str(row.get(key, "")))}</td>' for key in ['test_case_id', 'requirement_id', 'scenario_id', 'expected_json', 'actual_result', 'execution_status']) + '</tr>' for row in results)
    page = f'''<!DOCTYPE html><html><head><meta charset="utf-8"><title>EduCommerce Test Report</title><style>body{{font:15px Arial;margin:35px;color:#14233c}}h1{{color:#17385f}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #cbd5e1;padding:9px;text-align:left}}th{{background:#16385e;color:white}}tr:nth-child(even){{background:#f1f5f9}}.metric{{display:inline-block;margin:12px;padding:16px;border-radius:12px;background:#edf3f9;font-size:22px}}</style></head><body><h1>EduCommerce - Automated Test Execution</h1><div class="metric">Total: {len(df)}</div><div class="metric">PASS: {counts["PASS"]}</div><div class="metric">FAIL: {counts["FAIL"]}</div><h2>Traceability & Execution</h2><table><tr><th>Case</th><th>Requirement</th><th>Scenario</th><th>Expected</th><th>Actual</th><th>Status</th></tr>{rows}</table></body></html>'''
    (output / 'test_dashboard.html').write_text(page, encoding='utf-8')

    print(f'Executed {len(df)} | PASS {counts["PASS"]} | FAIL {counts["FAIL"]}')
    fail_df = df[df.execution_status == 'FAIL']
    if not fail_df.empty:
        print(fail_df[['test_case_id', 'expected_json', 'actual_result']].to_string(index=False))
    return df, output

if __name__ == '__main__':
    run_suite()
