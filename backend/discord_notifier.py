"""Discord webhook notification service for copy job events."""
import aiohttp
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class DiscordNotifier:
    """Sends rich embed notifications to Discord webhooks."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url
    
    def set_webhook_url(self, url: str):
        """Update the webhook URL."""
        self.webhook_url = url
    
    def format_size(self, bytes_size: int) -> str:
        """Format bytes to human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"
    
    def format_duration(self, seconds: float) -> str:
        """Format seconds to human-readable duration."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            mins = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{mins}m {secs}s"
        else:
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            return f"{hours}h {mins}m"
    
    async def send_job_notification(
        self,
        job_id: int,
        source_path: str,
        destination_path: str,
        status: str,
        total_size_bytes: int = 0,
        duration_seconds: float = 0,
        error_message: Optional[str] = None,
        media_title: Optional[str] = None,
        poster_url: Optional[str] = None
    ) -> bool:
        """
        Send a Discord notification for a copy job event.
        
        Returns True if successful, False otherwise.
        """
        if not self.webhook_url:
            logger.debug("No Discord webhook URL configured")
            return False
        
        try:
            # Determine embed properties based on status
            if status == "completed":
                color = 0x2ECC71  # Green
                title_prefix = "✅ Copy Completed"
            elif status == "failed":
                color = 0xE74C3C  # Red
                title_prefix = "❌ Copy Failed"
            elif status == "cancelled":
                color = 0xF39C12  # Yellow/Orange
                title_prefix = "⚠️ Copy Cancelled"
            else:
                return False  # Don't notify for other statuses
            
            # Use enriched title if available, otherwise generic message
            if media_title:
                description = f"**{media_title}** has finished {status if status != 'completed' else 'copying'}."
            else:
                description = f"Job #{job_id} {status if status != 'completed' else 'finished'} successfully."

            # Build fields
            fields = [
                {
                    "name": "📂 Source",
                    "value": f"```{source_path}```",
                    "inline": False
                },
                {
                    "name": "📁 Destination",
                    "value": f"```{destination_path}```",
                    "inline": False
                }
            ]
            
            # Add size and duration for completed jobs
            if total_size_bytes > 0:
                fields.append({
                    "name": "📦 Size",
                    "value": self.format_size(total_size_bytes),
                    "inline": True
                })
            
            if duration_seconds > 0:
                fields.append({
                    "name": "⏱️ Duration",
                    "value": self.format_duration(duration_seconds),
                    "inline": True
                })
                
                # Calculate and show speed for completed jobs
                if status == "completed" and total_size_bytes > 0:
                    speed = total_size_bytes / duration_seconds
                    fields.append({
                        "name": "🚀 Avg Speed",
                        "value": f"{self.format_size(int(speed))}/s",
                        "inline": True
                    })
            
            # Add error message for failed jobs
            if error_message and status == "failed":
                fields.append({
                    "name": "💥 Error",
                    "value": f"```{error_message[:500]}```",
                    "inline": False
                })
            
            # Build embed
            embed = {
                "title": title_prefix,
                "description": description,
                "color": color,
                "fields": fields,
                "footer": {
                    "text": "CopyCat • File Transfer Manager"
                },
                "timestamp": datetime.utcnow().isoformat()
            }

            # Add thumbnail if poster is available
            if poster_url:
                embed["thumbnail"] = {"url": poster_url}
            
            payload = {
                "embeds": [embed]
            }
            
            # Send to Discord
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 204:
                        logger.info(f"Discord notification sent for job {job_id}")
                        return True
                    else:
                        text = await response.text()
                        logger.error(f"Discord webhook failed: {response.status} - {text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")
            return False
    
    async def test_webhook(self) -> bool:
        """Send a test notification to verify webhook is working."""
        if not self.webhook_url:
            return False
        
        try:
            embed = {
                "title": "🔔 CopyCat Connected",
                "description": "Discord notifications are now enabled!",
                "color": 0x60CDFF,  # Cyan accent
                "fields": [
                    {
                        "name": "Status",
                        "value": "✅ Webhook verified successfully",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "CopyCat • File Transfer Manager"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            payload = {"embeds": [embed]}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    return response.status == 204
                    
        except Exception as e:
            logger.error(f"Discord test webhook failed: {e}")
            return False


# Global instance
discord_notifier = DiscordNotifier()

