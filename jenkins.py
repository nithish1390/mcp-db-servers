"""MCP server for triggering Jenkins jobs.

This server provides tools to trigger Jenkins jobs and query build status.

Configuration:
- JENKINS_URL: Jenkins base URL (e.g. https://jenkins.example.com)
- JENKINS_USER: Jenkins username
- JENKINS_TOKEN: Jenkins API token/password

Example usage (via MCP tool call):
{
  "tool": "trigger_job",
  "args": {
    "job_name": "my-job",
    "parameters": {"PARAM1": "value"}
  }
}
"""

from typing import Any, Dict, Optional

import requests

from mcp.server.fastmcp import Context, FastMCP


# Hard-coded Jenkins configuration (replace with your actual values)
JENKINS_URL = "https://jenkins.example.com"
JENKINS_USER = "your-username"
JENKINS_TOKEN = "your-token"

# Allowed jobs list (only these jobs may be triggered)
ALLOWED_JOBS = {
    "my-job",
    "another-job"
}


def _get_jenkins_auth() -> Optional[tuple[str, str]]:
    """Get Jenkins auth credentials from hard-coded configuration."""
    if JENKINS_USER and JENKINS_TOKEN:
        return (JENKINS_USER, JENKINS_TOKEN)
    return None


def _get_jenkins_url() -> str:
    """Get Jenkins base URL from hard-coded configuration."""
    if not JENKINS_URL:
        raise ValueError("JENKINS_URL is not configured")
    return JENKINS_URL.rstrip("/")


def _get_crumb(session: requests.Session, base_url: str, auth: Optional[tuple[str, str]]) -> Dict[str, str]:
    """Fetch Jenkins CSRF crumb."""
    crumb_url = f"{base_url}/crumbIssuer/api/json"
    resp = session.get(crumb_url, auth=auth, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return {data["crumbRequestField"]: data["crumb"]}


def trigger_jenkins_job(job_name: str, parameters: Optional[Dict[str, Any]] = None) -> str:
    """Trigger a Jenkins job and return the queue URL."""
    if job_name not in ALLOWED_JOBS:
        raise ValueError(f"Job '{job_name}' is not allowed. Allowed jobs: {sorted(ALLOWED_JOBS)}")

    base_url = _get_jenkins_url()
    auth = _get_jenkins_auth()

    # Build URL for job trigger
    job_path = job_name.replace("/", "/job/")
    trigger_url = f"{base_url}/job/{job_path}/build"
    if parameters:
        trigger_url += "WithParameters"

    session = requests.Session()
    headers: Dict[str, str] = {}

    if auth:
        headers.update(_get_crumb(session, base_url, auth))

    resp = session.post(trigger_url, auth=auth, headers=headers, params=parameters or {}, timeout=30)

    if resp.status_code not in (200, 201, 202):
        raise RuntimeError(f"Failed to trigger job: {resp.status_code} {resp.text}")

    # Jenkins returns queue location in header
    queue_url = resp.headers.get("Location") or resp.headers.get("location")
    return queue_url or "Triggered (no queue url returned)"


def get_job_status(job_name: str) -> str:
    """Get last build status for a Jenkins job."""
    base_url = _get_jenkins_url()
    auth = _get_jenkins_auth()

    job_path = job_name.replace("/", "/job/")
    status_url = f"{base_url}/job/{job_path}/lastBuild/api/json"

    resp = requests.get(status_url, auth=auth, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    return f"Last build: #{data.get('number')} status={data.get('result')} url={data.get('url')}"


# Create FastMCP server
mcp = FastMCP("Jenkins Trigger Server")


@mcp.tool()
def trigger_job(job_name: str, parameters: Optional[Dict[str, Any]] = None, ctx: Context = None) -> str:
    """Trigger a Jenkins job.

    Environment variables required:
      - JENKINS_URL
      - JENKINS_USER
      - JENKINS_TOKEN
    """
    try:
        return trigger_jenkins_job(job_name, parameters)
    except Exception as e:
        return f"Error triggering Jenkins job: {e}"


@mcp.tool()
def job_status(job_name: str, ctx: Context = None) -> str:
    """Get the latest build status for a Jenkins job."""
    try:
        return get_job_status(job_name)
    except Exception as e:
        return f"Error retrieving job status: {e}"


if __name__ == "__main__":
    mcp.run()
