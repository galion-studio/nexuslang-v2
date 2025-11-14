#!/usr/bin/env python3
"""
Test Report Generator for Galion Agent System

Generates comprehensive test reports in various formats (HTML, JSON, Markdown)
for CI/CD pipelines and development workflows.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import xml.etree.ElementTree as ET

import pytest
from coverage import Coverage
import jinja2


class TestReportGenerator:
    """Generates comprehensive test reports."""

    def __init__(self, output_dir: str = "test-reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now()

    def generate_html_report(self, test_results: Dict[str, Any], coverage_data: Dict[str, Any]) -> str:
        """Generate HTML test report."""
        template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Galion Test Report</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }
                .header h1 { margin: 0; font-size: 2.5em; }
                .header p { margin: 10px 0 0 0; opacity: 0.9; }
                .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 30px; }
                .metric { text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px; }
                .metric h3 { margin: 0 0 10px 0; color: #495057; font-size: 2em; }
                .metric p { margin: 0; color: #6c757d; text-transform: uppercase; font-size: 0.9em; letter-spacing: 1px; }
                .status-pass { color: #28a745; }
                .status-fail { color: #dc3545; }
                .status-warn { color: #ffc107; }
                .details { padding: 30px; }
                .section { margin-bottom: 40px; }
                .section h2 { color: #495057; border-bottom: 2px solid #e9ecef; padding-bottom: 10px; }
                .test-results { display: grid; gap: 10px; }
                .test-item { padding: 15px; border-radius: 6px; border-left: 4px solid; }
                .test-pass { background: #d4edda; border-left-color: #28a745; }
                .test-fail { background: #f8d7da; border-left-color: #dc3545; }
                .test-skip { background: #fff3cd; border-left-color: #ffc107; }
                .coverage { margin-top: 20px; }
                .coverage-bar { width: 100%; height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; }
                .coverage-fill { height: 100%; background: linear-gradient(90deg, #28a745, #20c997); transition: width 0.3s ease; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }
                th { background: #f8f9fa; font-weight: 600; }
                .footer { text-align: center; padding: 20px; color: #6c757d; border-top: 1px solid #e9ecef; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧪 Galion Test Report</h1>
                    <p>Generated on {{ timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</p>
                </div>

                <div class="summary">
                    <div class="metric">
                        <h3 class="{{ 'status-pass' if test_results.passed > 0 else 'status-fail' }}">{{ test_results.passed }}</h3>
                        <p>Tests Passed</p>
                    </div>
                    <div class="metric">
                        <h3 class="{{ 'status-fail' if test_results.failed > 0 else 'status-pass' }}">{{ test_results.failed }}</h3>
                        <p>Tests Failed</p>
                    </div>
                    <div class="metric">
                        <h3 class="status-warn">{{ test_results.skipped }}</h3>
                        <p>Tests Skipped</p>
                    </div>
                    <div class="metric">
                        <h3>{{ coverage_data.total_coverage }}%</h3>
                        <p>Code Coverage</p>
                    </div>
                </div>

                <div class="details">
                    <div class="section">
                        <h2>Test Results</h2>
                        <div class="test-results">
                            {% for test in test_results.tests %}
                            <div class="test-item test-{{ test.outcome.lower() }}">
                                <strong>{{ test.nodeid }}</strong>
                                {% if test.outcome == 'failed' %}
                                <br><small>Error: {{ test.error|truncate(100) }}</small>
                                {% endif %}
                                <br><small>Duration: {{ "%.3f"|format(test.duration) }}s</small>
                            </div>
                            {% endfor %}
                        </div>
                    </div>

                    <div class="section">
                        <h2>Coverage Report</h2>
                        <div class="coverage">
                            <div class="coverage-bar">
                                <div class="coverage-fill" style="width: {{ coverage_data.total_coverage }}%"></div>
                            </div>
                            <p style="text-align: center; margin-top: 10px;">
                                {{ coverage_data.total_coverage }}% coverage across {{ coverage_data.num_files }} files
                            </p>
                        </div>

                        <table>
                            <thead>
                                <tr>
                                    <th>File</th>
                                    <th>Statements</th>
                                    <th>Missing</th>
                                    <th>Coverage</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for file, data in coverage_data.files.items() %}
                                <tr>
                                    <td>{{ file }}</td>
                                    <td>{{ data.statements }}</td>
                                    <td>{{ data.missing }}</td>
                                    <td>
                                        <span style="color: {{ '#28a745' if data.coverage >= 80 else '#ffc107' if data.coverage >= 60 else '#dc3545' }}">
                                            {{ data.coverage }}%
                                        </span>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>

                    <div class="section">
                        <h2>Test Summary</h2>
                        <table>
                            <tbody>
                                <tr><td>Total Tests</td><td>{{ test_results.total }}</td></tr>
                                <tr><td>Passed</td><td>{{ test_results.passed }}</td></tr>
                                <tr><td>Failed</td><td>{{ test_results.failed }}</td></tr>
                                <tr><td>Skipped</td><td>{{ test_results.skipped }}</td></tr>
                                <tr><td>Duration</td><td>{{ "%.2f"|format(test_results.duration) }}s</td></tr>
                                <tr><td>Success Rate</td><td>{{ "%.1f"|format((test_results.passed / test_results.total * 100) if test_results.total > 0 else 0) }}%</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="footer">
                    <p>Report generated by Galion Test Suite • {{ timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</p>
                </div>
            </div>
        </body>
        </html>
        """

        env = jinja2.Environment()
        template_obj = env.from_string(template)

        html_content = template_obj.render(
            test_results=test_results,
            coverage_data=coverage_data,
            timestamp=self.timestamp
        )

        output_file = self.output_dir / "test-report.html"
        output_file.write_text(html_content)

        return str(output_file)

    def generate_json_report(self, test_results: Dict[str, Any], coverage_data: Dict[str, Any]) -> str:
        """Generate JSON test report."""
        report = {
            "metadata": {
                "generated_at": self.timestamp.isoformat(),
                "generator": "Galion Test Report Generator",
                "version": "1.0.0"
            },
            "test_results": test_results,
            "coverage": coverage_data,
            "summary": {
                "total_tests": test_results.get("total", 0),
                "passed": test_results.get("passed", 0),
                "failed": test_results.get("failed", 0),
                "skipped": test_results.get("skipped", 0),
                "success_rate": (test_results.get("passed", 0) / test_results.get("total", 1)) * 100,
                "total_coverage": coverage_data.get("total_coverage", 0),
                "duration": test_results.get("duration", 0)
            }
        }

        output_file = self.output_dir / "test-report.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        return str(output_file)

    def generate_markdown_report(self, test_results: Dict[str, Any], coverage_data: Dict[str, Any]) -> str:
        """Generate Markdown test report."""
        md_content = f"""# 🧪 Galion Test Report

Generated on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Summary

| Metric | Value |
|--------|-------|
| Total Tests | {test_results.get('total', 0)} |
| Passed | {test_results.get('passed', 0)} ✅ |
| Failed | {test_results.get('failed', 0)} ❌ |
| Skipped | {test_results.get('skipped', 0)} ⚠️ |
| Success Rate | {((test_results.get('passed', 0) / test_results.get('total', 1)) * 100):.1f}% |
| Code Coverage | {coverage_data.get('total_coverage', 0)}% |
| Duration | {test_results.get('duration', 0):.2f}s |

## 🧪 Test Results

### Passed Tests ({test_results.get('passed', 0)})
"""

        for test in test_results.get('tests', []):
            if test.get('outcome') == 'passed':
                md_content += f"- ✅ {test.get('nodeid')} ({test.get('duration', 0):.3f}s)\n"

        md_content += f"\n### Failed Tests ({test_results.get('failed', 0)})\n"

        for test in test_results.get('tests', []):
            if test.get('outcome') == 'failed':
                md_content += f"- ❌ {test.get('nodeid')} ({test.get('duration', 0):.3f}s)\n"
                if test.get('error'):
                    md_content += f"  - Error: {test.get('error')[:100]}...\n"

        md_content += f"\n### Skipped Tests ({test_results.get('skipped', 0)})\n"

        for test in test_results.get('tests', []):
            if test.get('outcome') == 'skipped':
                md_content += f"- ⚠️ {test.get('nodeid')}\n"

        md_content += f"\n## 📈 Coverage Report\n\n"
        md_content += f"**Overall Coverage: {coverage_data.get('total_coverage', 0)}%**\n\n"

        md_content += "| File | Statements | Missing | Coverage |\n"
        md_content += "|------|------------|---------|----------|\n"

        for file, data in coverage_data.get('files', {}).items():
            md_content += f"| {file} | {data.get('statements', 0)} | {data.get('missing', 0)} | {data.get('coverage', 0)}% |\n"

        md_content += "\n---\n\n"
        md_content += "*Report generated by Galion Test Suite*"

        output_file = self.output_dir / "test-report.md"
        output_file.write_text(md_content)

        return str(output_file)

    def parse_pytest_results(self, junit_xml: str) -> Dict[str, Any]:
        """Parse pytest JUnit XML results."""
        tree = ET.parse(junit_xml)
        root = tree.getroot()

        results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'duration': 0.0,
            'tests': []
        }

        for testsuite in root:
            for testcase in testsuite:
                results['total'] += 1
                duration = float(testcase.get('time', 0))
                results['duration'] += duration

                test_info = {
                    'nodeid': f"{testcase.get('classname', '')}.{testcase.get('name', '')}",
                    'duration': duration,
                    'outcome': 'passed'
                }

                # Check for failure
                failure = testcase.find('failure')
                if failure is not None:
                    results['failed'] += 1
                    test_info['outcome'] = 'failed'
                    test_info['error'] = failure.text or "Test failed"

                # Check for skip
                skip = testcase.find('skipped')
                if skip is not None:
                    results['skipped'] += 1
                    test_info['outcome'] = 'skipped'
                elif failure is None:
                    results['passed'] += 1

                results['tests'].append(test_info)

        return results

    def parse_coverage_results(self, coverage_xml: str) -> Dict[str, Any]:
        """Parse coverage XML results."""
        tree = ET.parse(coverage_xml)
        root = tree.getroot()

        coverage_data = {
            'total_coverage': 0.0,
            'num_files': 0,
            'files': {}
        }

        # Parse overall coverage
        for package in root.findall('.//package'):
            for classes in package.findall('classes'):
                for class_elem in classes.findall('class'):
                    filename = class_elem.get('filename', '')
                    if filename.startswith('v2/'):  # Only include our code
                        statements = int(class_elem.get('statements', 0))
                        missing = int(class_elem.get('missing', 0))
                        coverage = float(class_elem.get('coverage', 0))

                        coverage_data['files'][filename] = {
                            'statements': statements,
                            'missing': missing,
                            'coverage': coverage
                        }

                        coverage_data['num_files'] += 1

        # Calculate total coverage
        if coverage_data['files']:
            total_statements = sum(f['statements'] for f in coverage_data['files'].values())
            total_missing = sum(f['missing'] for f in coverage_data['files'].values())

            if total_statements > 0:
                coverage_data['total_coverage'] = round(
                    ((total_statements - total_missing) / total_statements) * 100, 1
                )

        return coverage_data

    def generate_all_reports(self, junit_xml: str = "junit.xml",
                           coverage_xml: str = "coverage.xml") -> Dict[str, str]:
        """Generate all report formats."""
        reports = {}

        try:
            # Parse test results
            test_results = self.parse_pytest_results(junit_xml)

            # Parse coverage results
            coverage_data = self.parse_coverage_results(coverage_xml)

            # Generate reports
            reports['html'] = self.generate_html_report(test_results, coverage_data)
            reports['json'] = self.generate_json_report(test_results, coverage_data)
            reports['markdown'] = self.generate_markdown_report(test_results, coverage_data)

            print(f"✅ Generated test reports in {self.output_dir}")
            for format_name, file_path in reports.items():
                print(f"  {format_name.upper()}: {file_path}")

        except Exception as e:
            print(f"❌ Error generating reports: {e}")
            reports['error'] = str(e)

        return reports


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate Galion test reports")
    parser.add_argument("--junit-xml", default="junit.xml", help="Path to pytest JUnit XML file")
    parser.add_argument("--coverage-xml", default="coverage.xml", help="Path to coverage XML file")
    parser.add_argument("--output-dir", default="test-reports", help="Output directory for reports")

    args = parser.parse_args()

    generator = TestReportGenerator(args.output_dir)
    reports = generator.generate_all_reports(args.junit_xml, args.coverage_xml)

    if 'error' not in reports:
        print("\n🎉 All reports generated successfully!")
        return 0
    else:
        print(f"\n❌ Report generation failed: {reports['error']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
