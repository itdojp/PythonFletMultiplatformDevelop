#!/usr/bin/env python3
"""
Performance Alerting System

This script analyzes performance test results and sends alerts if performance degrades.
"""

import json
import logging
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PerformanceAlert:
    """Send alerts when performance degrades below thresholds."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the alerting system.

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.results_dir = Path(self.config.get("results_dir", "results"))
        self.thresholds = self.config.get("thresholds", {})

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults.

        Args:
            config_path: Path to configuration file

        Returns:
            Dictionary with configuration
        """
        default_config = {
            "results_dir": "results",
            "thresholds": {
                "response_time_p95": 1000,  # ms
                "error_rate": 0.01,  # 1%
                "throughput": 10,  # req/s
            },
            "alerting": {
                "enabled": True,
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.example.com",
                    "smtp_port": 587,
                    "username": "user@example.com",
                    "password": "password",
                    "from_addr": "alerts@example.com",
                    "to_addrs": ["team@example.com"],
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": "https://hooks.slack.com/services/...",
                    "channel": "#alerts",
                },
            },
        }

        if config_path and Path(config_path).exists():
            try:
                with open(config_path, "r") as f:
                    import yaml

                    config = yaml.safe_load(f)
                    # Merge with default config
                    default_config.update(config)
            except Exception as e:
                logger.error(f"Failed to load config from {config_path}: {e}")

        return default_config

    def analyze_test_results(self, test_name: str) -> Dict[str, Any]:
        """Analyze test results and check against thresholds.

        Args:
            test_name: Name of the test to analyze

        Returns:
            Dictionary with analysis results and alerts
        """
        result_file = self.results_dir / f"{test_name}_results.json"
        if not result_file.exists():
            return {
                "status": "error",
                "message": f"Results file not found: {result_file}",
            }

        try:
            with open(result_file, "r") as f:
                results = json.load(f)

            # Extract metrics
            stats = results.get("stats", [])
            if not stats:
                return {"status": "error", "message": "No statistics found in results"}

            # Check each endpoint against thresholds
            alerts = []
            for endpoint in stats:
                endpoint_name = endpoint.get("name", "unknown")
                p95 = endpoint.get("response_time_percentile_95", 0)
                error_rate = endpoint.get("fail_ratio", 0)
                rps = endpoint.get("total_rps", 0)

                # Check thresholds
                if p95 > self.thresholds.get("response_time_p95", 1000):
                    alerts.append(
                        {
                            "endpoint": endpoint_name,
                            "metric": "response_time_p95",
                            "value": p95,
                            "threshold": self.thresholds["response_time_p95"],
                            "message": f'Response time P95 ({p95}ms) exceeds threshold ({self.thresholds["response_time_p95"]}ms)',
                        }
                    )

                if error_rate > self.thresholds.get("error_rate", 0.01):
                    alerts.append(
                        {
                            "endpoint": endpoint_name,
                            "metric": "error_rate",
                            "value": error_rate * 100,  # Convert to percentage
                            "threshold": self.thresholds["error_rate"] * 100,
                            "message": f'Error rate ({error_rate*100:.2f}%) exceeds threshold ({self.thresholds["error_rate"]*100}%)',
                        }
                    )

                if rps < self.thresholds.get("throughput", 10):
                    alerts.append(
                        {
                            "endpoint": endpoint_name,
                            "metric": "throughput",
                            "value": rps,
                            "threshold": self.thresholds["throughput"],
                            "message": f'Throughput ({rps:.2f} req/s) below threshold ({self.thresholds["throughput"]} req/s)',
                        }
                    )

            return {
                "status": "success",
                "test_name": test_name,
                "timestamp": datetime.now().isoformat(),
                "alerts": alerts,
                "metrics": {
                    "endpoints": stats,
                    "summary": {
                        "total_requests": sum(e.get("num_requests", 0) for e in stats),
                        "total_failures": sum(e.get("num_failures", 0) for e in stats),
                        "avg_response_time": sum(
                            e.get("avg_response_time", 0) * e.get("num_requests", 0)
                            for e in stats
                        )
                        / max(1, sum(e.get("num_requests", 1) for e in stats)),
                        "total_rps": sum(e.get("total_rps", 0) for e in stats),
                    },
                },
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to analyze results: {str(e)}",
            }

    def send_alert(self, analysis_result: Dict[str, Any]) -> bool:
        """Send alerts based on analysis results.

        Args:
            analysis_result: Results from analyze_test_results

        Returns:
            bool: True if alerts were sent successfully
        """
        if not analysis_result.get("alerts"):
            logger.info("No alerts to send")
            return True

        alerting_config = self.config.get("alerting", {})
        if not alerting_config.get("enabled", False):
            logger.info("Alerting is disabled")
            return False

        success = True

        # Send email alert if configured
        if alerting_config.get("email", {}).get("enabled", False):
            success &= self._send_email_alert(analysis_result)

        # Send Slack alert if configured
        if alerting_config.get("slack", {}).get("enabled", False):
            success &= self._send_slack_alert(analysis_result)

        return success

    def _send_email_alert(self, analysis_result: Dict[str, Any]) -> bool:
        """Send alert via email.

        Args:
            analysis_result: Analysis results

        Returns:
            bool: True if email was sent successfully
        """
        email_config = self.config["alerting"]["email"]

        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = email_config["from_addr"]
            msg["To"] = ", ".join(email_config["to_addrs"])
            msg["Subject"] = (
                f"[ALERT] Performance Degradation - {analysis_result['test_name']}"
            )

            # Create email body
            body = f"""
            Performance Alert
            =================

            Test: {analysis_result['test_name']}
            Timestamp: {analysis_result['timestamp']}

            Alerts:
            -------
            """

            for alert in analysis_result["alerts"]:
                body += f"- {alert['message']}\n"

            # Add summary
            body += f"""

            Summary:
            --------
            Total Requests: {analysis_result['metrics']['summary']['total_requests']}
            Total Failures: {analysis_result['metrics']['summary']['total_failures']}
            Avg Response Time: {analysis_result['metrics']['summary']['avg_response_time']:.2f} ms
            Requests/sec: {analysis_result['metrics']['summary']['total_rps']:.2f}
            """

            msg.attach(MIMEText(body, "plain"))

            # Send email
            with smtplib.SMTP(
                email_config["smtp_server"], email_config["smtp_port"]
            ) as server:
                server.starttls()
                server.login(email_config["username"], email_config["password"])
                server.send_message(msg)

            logger.info(f"Email alert sent to {email_config['to_addrs']}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False

    def _send_slack_alert(self, analysis_result: Dict[str, Any]) -> bool:
        """Send alert to Slack.

        Args:
            analysis_result: Analysis results

        Returns:
            bool: True if message was sent successfully
        """
        slack_config = self.config["alerting"]["slack"]

        try:
            # Format message
            alert_count = len(analysis_result["alerts"])
            message = {
                "channel": slack_config["channel"],
                "username": "Performance Bot",
                "icon_emoji": ":warning:",
                "attachments": [
                    {
                        "color": "danger",
                        "title": f'Performance Alert: {analysis_result["test_name"]}',
                        "text": f"*{alert_count} performance issue(s) detected*",
                        "fields": [
                            {
                                "title": "Issues",
                                "value": "\n".join(
                                    [
                                        f"• {alert['message']}"
                                        for alert in analysis_result["alerts"]
                                    ]
                                ),
                                "short": False,
                            },
                            {
                                "title": "Summary",
                                "value": (
                                    f"• Total Requests: {analysis_result['metrics']['summary']['total_requests']}\n"
                                    f"• Failures: {analysis_result['metrics']['summary']['total_failures']}\n"
                                    f"• Avg Response: {analysis_result['metrics']['summary']['avg_response_time']:.2f} ms\n"
                                    f"• RPS: {analysis_result['metrics']['summary']['total_rps']:.2f}"
                                ),
                                "short": False,
                            },
                        ],
                        "footer": f'Timestamp: {analysis_result["timestamp"]}',
                        "ts": datetime.now().timestamp(),
                    }
                ],
            }

            # Send to Slack
            response = requests.post(
                slack_config["webhook_url"],
                json=message,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            logger.info("Slack alert sent successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False


def main():
    """Main function to run the performance alerting."""
    import argparse

    parser = argparse.ArgumentParser(description="Performance Alerting System")
    parser.add_argument("test_name", help="Name of the test to analyze")
    parser.add_argument("--config", "-c", help="Path to configuration file")
    args = parser.parse_args()

    # Initialize alerting system
    alert_system = PerformanceAlert(args.config)

    # Analyze test results
    analysis = alert_system.analyze_test_results(args.test_name)

    if analysis["status"] != "success":
        logger.error(
            f"Failed to analyze test results: {analysis.get('message', 'Unknown error')}"
        )
        return 1

    # Send alerts if needed
    if analysis["alerts"]:
        logger.warning(f"Found {len(analysis['alerts'])} performance issues")
        alert_system.send_alert(analysis)
    else:
        logger.info("No performance issues detected")

    return 0


if __name__ == "__main__":
    exit(main())
