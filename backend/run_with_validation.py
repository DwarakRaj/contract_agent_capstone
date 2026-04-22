import os
import sys
import argparse
import uvicorn
from dotenv import load_dotenv

# Ensure backend is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.shared.monitoring.build_validator import BuildValidator
import uuid
from backend.shared.utils.logger import get_logger, setup_logging, set_correlation_id

# Load environment variables
load_dotenv()

# Initialize logging for the validator
setup_logging()
logger = get_logger("StartupGatekeeper")

def main():
    """
    Main entry point for starting the application with mandatory build validation.
    """
    parser = argparse.ArgumentParser(description="Run the application with build validation.")
    parser.add_argument("--force", action="store_true", help="Force run unit tests even if no changes detected.")
    args = parser.parse_args()

    # Initialize request tracing for the build validation phase
    build_id = f"build-{uuid.uuid4().hex[:8]}"
    set_correlation_id(build_id)
    
    logger.info(f"Initializing Agentic Build Validation Gatekeeper (Build ID: {build_id})...")
    
    # Root directory is the project root
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # We want to run tests relative to the backend directory where pytest.ini is
    backend_dir = os.path.join(root_dir, "backend")
    
    validator = BuildValidator(backend_dir)
    
    # Target port from environment or default 8000
    port = int(os.environ.get("PORT", 8000))
    
    # Perform validation
    success = validator.validate_all(port_check=port, force_unit=args.force)
    
    if not success:
        logger.error("SYSTEM BREACH PREVENTION: Validation Failed. Application will not start.")
        logger.error(f"Detailed report generated at: {validator.report_path}")
        sys.exit(1)
        
    logger.info("Validation passed! Starting application...")
    
    # Start the application
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=False  # Typically False when running with a wrapper script
    )

if __name__ == "__main__":
    main()
