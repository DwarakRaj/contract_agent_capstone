import os
from datetime import datetime
from typing import List, Dict, Any

class TestReportGenerator:
    """
    Generates human-readable Markdown reports from test results.
    Adheres to the principle of clear communication and observability.
    """
    
    @staticmethod
    def generate_markdown_report(results: Dict[str, Dict[str, Any]], output_path: str):
        """
        Creates a detailed Markdown report summarizing multiple test stages.
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md_content = f"# Detailed Build Validation Report\n\n"
        md_content += f"**Generated At:** {now}  \n"
        
        overall_status = "PASSED ✅"
        for stage, data in results.items():
            if data.get("status") == "FAIL":
                overall_status = "FAILED ❌"
                break
        
        md_content += f"**Overall Status:** {overall_status}\n\n"
        md_content += "## Summary of Stages\n\n"
        md_content += "| Stage | Total | Passed | Failed | Status | Duration |\n"
        md_content += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        
        for stage, data in results.items():
            if data.get("status") == "PASS":
                status_emoji = "✅"
            elif data.get("status") == "SKIPPED":
                status_emoji = "⚡"
            else:
                status_emoji = "❌"
                
            md_content += f"| {stage.capitalize()} | {data.get('total', 0)} | {data.get('passed', 0)} | {data.get('failed', 0)} | {status_emoji} {data.get('status')} | {data.get('duration', 0)}s |\n"
        
        md_content += "\n---\n"
        
        # Details for failures
        has_failures = False
        for stage, data in results.items():
            if data.get("failed", 0) > 0:
                if not has_failures:
                    md_content += "## Error Details\n\n"
                    has_failures = True
                
                md_content += f"### {stage.capitalize()} Failures\n\n"
                for test in data.get("tests", []):
                    md_content += f"- **Test:** `{test['nodeid']}`\n"
                    md_content += f"  - **Duration:** {test['duration']}s\n"
                    md_content += f"  - **Error:**\n  ```\n  {test['error'][-500:]}\n  ```\n\n" # Limit error length

        if not has_failures:
            md_content += "## System Health\n\nAll components are verified and functioning correctly. The system is safe to start.\n"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return md_content
