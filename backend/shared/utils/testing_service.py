import pytest
import os
import json
from typing import List, Dict, Any, Optional
from backend.shared.utils.logger import get_logger

logger = get_logger(__name__)

class TestingService:
    """
    A centralized service for programmatically executing tests across different categories.
    Follows SOLID principles by decoupling test discovery from execution logic.
    """
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.reports_dir = os.path.join(root_dir, "reports")
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def run_tests_by_marker(self, marker: str) -> Dict[str, Any]:
        """
        Runs tests with the specified marker (unit, functional, integration, etc.)
        """
        logger.info(f"Starting execution of '{marker}' tests...")
        
        report_file = os.path.join(self.reports_dir, f"report_{marker}.json")
        html_file = os.path.join(self.reports_dir, f"report_{marker}.html")
        
        args = [
            "-m", marker,
            f"--json-report-file={report_file}",
            f"--html={html_file}",
            "--self-contained-html",
            "--json-report",
            "-v"
        ]
        
        # Change to root_dir for correct path discovery
        old_cwd = os.getcwd()
        try:
            # os.chdir(self.root_dir) # Antigravity guideline: NEVER PROPOSE A cd COMMAND.
            # Pytest can take the path as an argument.
            args.append(self.root_dir)
            
            exit_code = pytest.main(args)
            
            # Load the results from the JSON report if it exists
            result_summary = self._parse_json_report(report_file)
            result_summary["exit_code"] = int(exit_code)
            result_summary["status"] = "PASS" if exit_code == 0 else "FAIL"
            
            logger.info(f"Finished '{marker}' tests with status: {result_summary['status']}")
            return result_summary
            
        finally:
            pass # os.chdir(old_cwd)

    def _parse_json_report(self, report_path: str) -> Dict[str, Any]:
        """Helper to extract key metrics from pytest-json-report output."""
        try:
            if not os.path.exists(report_path):
                return {"error": "Report file not found", "total": 0, "passed": 0, "failed": 0}
                
            with open(report_path, 'r') as f:
                data = json.load(f)
                
            summary = data.get("summary", {})
            return {
                "total": summary.get("total", 0),
                "passed": summary.get("passed", 0),
                "failed": summary.get("failed", 0),
                "skipped": summary.get("skipped", 0),
                "duration": round(data.get("duration", 0), 2),
                "tests": self._extract_test_details(data.get("tests", []))
            }
        except Exception as e:
            logger.error(f"Failed to parse test report: {e}")
            return {"error": str(e), "total": 0, "passed": 0, "failed": 0}

    def _extract_test_details(self, test_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extracts significant details for failed tests."""
        details = []
        for test in test_list:
            if test.get("outcome") == "failed":
                details.append({
                    "nodeid": test.get("nodeid"),
                    "duration": round(test.get("duration", 0), 3),
                    "error": test.get("setup", {}).get("longrepr", "") or test.get("call", {}).get("longrepr", "")
                })
        return details
