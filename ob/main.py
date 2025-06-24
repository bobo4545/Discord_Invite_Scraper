import os
import json
import time
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Tuple, Set

import tls_client
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init(autoreset=True)

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("verification_bypass.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("VerificationBypass")

# ASCII Art Banner
BANNER = f"""
{Fore.CYAN}
 ██████╗ ██╗███████╗ ██████╗ ██████╗ ██████╗ ██████╗     ██████╗ ██╗   ██╗██████╗  █████╗ ███████╗███████╗
 ██╔══██╗██║██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔══██╗    ██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗██╔════╝██╔════╝
 ██║  ██║██║███████╗██║     ██║   ██║██████╔╝██║  ██║    ██████╔╝ ╚████╔╝ ██████╔╝███████║███████╗███████╗
 ██║  ██║██║╚════██║██║     ██║   ██║██╔══██╗██║  ██║    ██╔══██╗  ╚██╔╝  ██╔═══╝ ██╔══██║╚════██║╚════██║
 ██████╔╝██║███████║╚██████╗╚██████╔╝██║  ██║██████╔╝    ██████╔╝   ██║   ██║     ██║  ██║███████║███████║
 ╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝     ╚═════╝    ╚═╝   ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝
                                                                                   
{Fore.LIGHTCYAN_EX}Discord Verification Bypass Tool - Onboarding & TOS{Style.RESET_ALL}
"""

class Config:
    """Handles loading configuration and resources"""
    
    def __init__(self):
        self.settings = {}
        self.proxies = []
        self.tokens = []
        
    def load(self) -> bool:
        """Load configuration files and resources"""
        try:
            # Load config file
            if os.path.exists("input/config.json"):
                with open("input/config.json") as f:
                    self.settings = json.load(f)
            else:
                # Default settings if no config file exists
                self.settings = {
                    "Threads": 5,
                    "Proxyless": False,
                    "Debug": False,
                    "ServerDelayMin": 9,  # Minimum delay between servers in seconds
                    "ServerDelayMax": 11  # Maximum delay between servers in seconds
                }
            
            # Load proxies
            self.proxies = self._load_proxies("input/proxies.txt")
            
            # Load tokens
            self.tokens = self._load_tokens("input/tokens.txt")
            
            logger.info(f"Configuration loaded: {len(self.tokens)} tokens, "
                        f"{len(self.proxies)} proxies, "
                        f"{self.settings.get('Threads', 5)} threads")
            
            return len(self.tokens) > 0
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            return False
    
    def _load_proxies(self, path: str) -> List[str]:
        """Load and format proxies from file"""
        proxies = []
        if not os.path.exists(path):
            logger.warning(f"Proxy file not found: {path}")
            return proxies
            
        try:
            with open(path, "r") as f:
                for line in f:
                    proxy = line.strip()
                    if proxy:
                        if not proxy.startswith("http"):
                            proxy = f"http://{proxy}"
                        proxies.append(proxy)
            return proxies
        except Exception as e:
            logger.error(f"Error loading proxies: {str(e)}")
            return []
    
    def _load_tokens(self, path: str) -> List[str]:
        """Load Discord tokens from file"""
        tokens = []
        if not os.path.exists(path):
            logger.warning(f"Token file not found: {path}")
            return tokens
            
        try:
            with open(path, "r") as f:
                for line in f:
                    token = line.strip()
                    if token:
                        # Handle token:secret format by extracting just the token part
                        if ":" in token:
                            token = token.split(":")[-1]
                        tokens.append(token)
            return tokens
        except Exception as e:
            logger.error(f"Error loading tokens: {str(e)}")
            return []


class DiscordSession:
    """Manages Discord API sessions"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client_identifier = "chrome_133"  # Chrome browser fingerprint
    
    def create(self, token: str = None) -> tls_client.Session:
        """Create a configured TLS session with optional token"""
        session = tls_client.Session(
            client_identifier=self.client_identifier,
            random_tls_extension_order=True
        )
        
        # Set standard Discord headers
        session.headers = self._generate_headers()
        
        # Add token if provided
        if token:
            session.headers["authorization"] = token
        
        # Apply proxy if enabled and available
        if not self.config.settings.get("Proxyless", False) and self.config.proxies:
            proxy = random.choice(self.config.proxies)
            session.proxies = {
                "http": proxy,
                "https": proxy
            }
            if self.config.settings.get("Debug", False):
                logger.debug(f"Using proxy: {proxy}")
        
        return session
    
    def _generate_headers(self) -> Dict[str, str]:
        """Generate modern Discord client headers"""
        return {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'referer': 'https://discord.com/',
            'sec-ch-ua': '"Google Chrome";v="133", "Chromium";v="133", "Not-A.Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-US',
            'x-discord-timezone': 'UTC',
            'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzMy4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTMzLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjIzNDU2NywiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0='
        }


class GuildManager:
    """Manages guild-related operations"""
    
    def __init__(self, session: tls_client.Session):
        self.session = session
    
    def get_user_guilds(self) -> List[Dict[str, Any]]:
        """Get all guilds the user is a member of"""
        try:
            response = self.session.get("https://discord.com/api/v9/users/@me/guilds")
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch guilds: Status {response.status_code}")
                return []
            
            guilds = response.json()
            logger.info(f"Found {len(guilds)} guilds for this user")
            return guilds
            
        except Exception as e:
            logger.error(f"Error fetching guilds: {str(e)}")
            return []
    
    def check_onboarding_required(self, guild_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Check if a guild requires onboarding"""
        try:
            response = self.session.get(f"https://discord.com/api/v9/guilds/{guild_id}/onboarding")
            
            if response.status_code == 404:
                return False, None
                
            if response.status_code == 403:
                logger.debug(f"No access to guild {guild_id} onboarding")
                return False, None
                
            if response.status_code != 200:
                logger.warning(f"Failed to check onboarding for guild {guild_id}: Status {response.status_code}")
                return False, None
            
            data = response.json()
            
            # Check if there are onboarding prompts
            if not data.get("prompts") or len(data.get("prompts", [])) == 0:
                return False, None
                
            return True, data
            
        except Exception as e:
            logger.error(f"Error checking onboarding for guild {guild_id}: {str(e)}")
            return False, None
    
    def check_tos_required(self, guild_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Check if a guild requires TOS acceptance"""
        try:
            response = self.session.get(
                f"https://discord.com/api/v9/guilds/{guild_id}/member-verification",
                params={'with_guild': 'false'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and (data.get('form_fields') or data.get('description')):
                    return True, data
                return False, None
                
            elif response.status_code == 403:
                logger.debug(f"No access to guild {guild_id} TOS verification")
                return False, None
                
            elif response.status_code == 404:
                return False, None
                
            elif response.status_code == 410:
                logger.debug(f"User already accepted TOS for guild {guild_id}")
                return False, None
                
            else:
                logger.warning(f"Failed to check TOS for guild {guild_id}: Status {response.status_code}")
                return False, None
            
        except Exception as e:
            logger.error(f"Error checking TOS for guild {guild_id}: {str(e)}")
            return False, None
    
    def get_guild_info(self, guild_id: str) -> Optional[Dict[str, Any]]:
        """Get guild information by ID"""
        try:
            response = self.session.get(f"https://discord.com/api/v9/guilds/{guild_id}")
            
            if response.status_code != 200:
                return None
                
            return response.json()
        except Exception:
            return None


class ManualVerificationTracker:
    """Tracks servers that need manual verification"""
    
    VERIFICATION_FILE = "manual_verification_needed.txt"
    
    @classmethod
    def add_guild(cls, guild_id: str, guild_name: str, error_reason: str, token_hint: str) -> None:
        """Add a guild to the manual verification list"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with open(cls.VERIFICATION_FILE, "a", encoding="utf-8") as f:
                f.write(f"===== Guild Added: {timestamp} =====\n")
                f.write(f"Guild ID: {guild_id}\n")
                f.write(f"Guild Name: {guild_name}\n")
                f.write(f"Error: {error_reason}\n")
                f.write(f"Token Hint: {token_hint}\n\n")
                
            logger.info(f"Added guild '{guild_name}' to manual verification list")
        except Exception as e:
            logger.error(f"Failed to add guild to verification list: {str(e)}")
    
    @classmethod
    def save_summary(cls, guilds: Dict[str, Dict[str, Any]]) -> None:
        """Save a summary file with all guilds that need manual verification"""
        try:
            if not guilds:
                return
                
            with open("verification_summary.txt", "w", encoding="utf-8") as f:
                f.write(f"===== Manual Verification Summary =====\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Guilds Requiring Verification: {len(guilds)}\n\n")
                
                for guild_id, info in guilds.items():
                    f.write(f"Guild ID: {guild_id}\n")
                    f.write(f"Guild Name: {info.get('name', 'Unknown')}\n")
                    f.write(f"Error: {info.get('error', 'Unknown error')}\n")
                    f.write(f"Affected Tokens: {len(info.get('tokens', []))}\n")
                    f.write("\n")
                    
            logger.info(f"Saved verification summary with {len(guilds)} guilds")
        except Exception as e:
            logger.error(f"Failed to save verification summary: {str(e)}")


class VerificationBypass:
    """Handles Discord server verification bypass logic"""
    
    def __init__(self, config: Config):
        self.config = config
        self.session_factory = DiscordSession(config)
        self.manual_verification_needed = {}  # Guild ID -> {name, error, tokens[]}
        # Statistics tracking
        self.stats = {
            "onboarding_bypassed": 0,
            "tos_accepted": 0,
            "already_verified": 0,
            "failed": 0,
            "no_access": 0,
            "phone_verification_required": 0
        }
    
    def process_all_guilds(self) -> None:
        """Process all guilds for all tokens to find and bypass verification"""
        if not self.config.tokens:
            logger.error("No tokens available to process")
            return
        
        logger.info(f"Starting automatic verification bypass for all guilds")
        logger.info(f"Will process {len(self.config.tokens)} tokens")
        
        for i, token in enumerate(self.config.tokens):
            masked_token = token[-5:].rjust(len(token), '*')
            logger.info(f"Processing token {i+1}/{len(self.config.tokens)}: {masked_token}")
            
            try:
                self.process_token_guilds(token)
            except Exception as e:
                logger.error(f"Failed to process token {masked_token}: {str(e)}")
        
        # Display stats summary
        logger.info(f"===== Verification Stats =====")
        logger.info(f"Onboarding Bypassed: {self.stats['onboarding_bypassed']}")
        logger.info(f"TOS Accepted: {self.stats['tos_accepted']}")
        logger.info(f"Already Verified: {self.stats['already_verified']}")
        logger.info(f"Failed: {self.stats['failed']}")
        logger.info(f"No Access: {self.stats['no_access']}")
        logger.info(f"Phone Verification Required: {self.stats['phone_verification_required']}")
        
        # Save summary of guilds needing verification
        if self.manual_verification_needed:
            logger.info(f"Found {len(self.manual_verification_needed)} guilds requiring manual verification")
            ManualVerificationTracker.save_summary(self.manual_verification_needed)
        else:
            logger.info("No guilds require manual verification")
            
        logger.info("Completed processing all tokens")
    
    def process_token_guilds(self, token: str) -> None:
        """Process all guilds for a specific token"""
        session = self.session_factory.create(token)
        guild_manager = GuildManager(session)
        token_hint = token[-5:].rjust(10, '*')
        
        # Get all guilds for this token
        guilds = guild_manager.get_user_guilds()
        if not guilds:
            logger.warning(f"No guilds found for token ending with {token[-5:]}")
            return
        
        logger.info(f"Found {len(guilds)} guilds for token ending with {token[-5:]}")
        
        # Modified: Directly attempt to bypass verification for all guilds without checking first
        for i, guild in enumerate(guilds):
            guild_id = guild["id"]
            guild_name = guild["name"]
            
            try:
                logger.info(f"Processing guild '{guild_name}' ({guild_id}) - {i+1}/{len(guilds)}")
                
                # Try to directly bypass onboarding
                onboarding_data = None
                try:
                    # Attempt to get onboarding data
                    onboarding_response = session.get(f"https://discord.com/api/v9/guilds/{guild_id}/onboarding")
                    if onboarding_response.status_code == 200:
                        onboarding_data = onboarding_response.json()
                except Exception as e:
                    logger.debug(f"Error getting onboarding data: {str(e)}")
                
                # Attempt onboarding bypass regardless of prior check
                if onboarding_data:
                    logger.info(f"Attempting onboarding for guild '{guild_name}'")
                    success, error_message = self._complete_onboarding(session, guild_id, guild_name, onboarding_data)
                    
                    if success:
                        logger.info(f"Successfully bypassed onboarding for guild '{guild_name}'")
                        self.stats["onboarding_bypassed"] += 1
                    else:
                        logger.warning(f"Failed to bypass onboarding for guild '{guild_name}': {error_message}")
                        if "already completed" in error_message.lower() or "no verification" in error_message.lower():
                            self.stats["already_verified"] += 1
                        else:
                            self._handle_error(guild_id, guild_name, error_message, token_hint)
                
                # Try to directly bypass TOS
                tos_data = None
                try:
                    # Attempt to get TOS data
                    tos_response = session.get(
                        f"https://discord.com/api/v9/guilds/{guild_id}/member-verification",
                        params={'with_guild': 'false'}
                    )
                    if tos_response.status_code == 200:
                        tos_data = tos_response.json()
                except Exception as e:
                    logger.debug(f"Error getting TOS data: {str(e)}")
                
                # Attempt TOS bypass regardless of prior check
                if tos_data:
                    logger.info(f"Attempting TOS acceptance for guild '{guild_name}'")
                    success, error_message = self._complete_tos_acceptance(session, guild_id, guild_name, tos_data)
                    
                    if success:
                        logger.info(f"Successfully accepted TOS for guild '{guild_name}'")
                        self.stats["tos_accepted"] += 1
                    else:
                        logger.warning(f"Failed to accept TOS for guild '{guild_name}': {error_message}")
                        if "already accepted" in error_message.lower() or "no verification" in error_message.lower():
                            self.stats["already_verified"] += 1
                        else:
                            self._handle_error(guild_id, guild_name, error_message, token_hint)
                
                # If we didn't attempt either bypass, the server is probably already verified
                if not onboarding_data and not tos_data:
                    logger.info(f"Guild '{guild_name}' doesn't need verification or is already verified")
                    self.stats["already_verified"] += 1
                
                # Add random delay between guild processing (only if not the last guild)
                if i < len(guilds) - 1:
                    delay = random.uniform(
                        self.config.settings.get("ServerDelayMin", 9),
                        self.config.settings.get("ServerDelayMax", 11)
                    )
                    logger.debug(f"Waiting {delay:.2f} seconds before processing next guild...")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error processing guild '{guild_name}' ({guild_id}): {str(e)}")
                self.stats["failed"] += 1
    
    def bypass_for_guild(self, guild_id: str) -> None:
        """Process all tokens to bypass verification for a specific guild"""
        if not guild_id or not guild_id.isdigit():
            logger.error("Invalid Guild ID provided")
            return
        
        if not self.config.tokens:
            logger.error("No tokens available to process")
            return
        
        logger.info(f"Starting verification bypass for guild {guild_id}")
        logger.info(f"Processing {len(self.config.tokens)} tokens with "
                   f"{self.config.settings.get('Threads', 5)} threads")
        
        # Use thread pool for parallel processing
        thread_count = min(self.config.settings.get("Threads", 5), len(self.config.tokens))
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = {
                executor.submit(self._process_token_for_guild, token, guild_id): token 
                for token in self.config.tokens
            }
            
            completed = 0
            successful = 0
            failed = 0
            
            for future in as_completed(futures):
                token = futures[future]
                token_hint = token[-5:].rjust(10, '*')
                
                try:
                    result, guild_name = future.result()
                    completed += 1
                    
                    if result:
                        successful += 1
                    else:
                        failed += 1
                    
                    # Progress update
                    if completed % 5 == 0 or completed == len(self.config.tokens):
                        progress = (completed / len(self.config.tokens)) * 100
                        logger.info(f"Progress: {progress:.1f}% ({completed}/{len(self.config.tokens)}) "
                                   f"- Success: {successful}, Failed: {failed}")
                        
                except Exception as e:
                    failed += 1
                    logger.error(f"Error processing token {token[-5:]}: {str(e)}")
        
        # Save summary
        if self.manual_verification_needed:
            logger.info(f"Found {len(self.manual_verification_needed)} tokens requiring manual verification")
            ManualVerificationTracker.save_summary(self.manual_verification_needed)
        
        # Update stats
        self.stats["failed"] += failed
        logger.info(f"Completed verification bypass: {successful} successful, {failed} failed")
    
    def _process_token_for_guild(self, token: str, guild_id: str) -> Tuple[bool, str]:
        """Process a single token to bypass verification for a specific guild
        
        Returns:
            (success, guild_name)
        """
        masked_token = token[-5:].rjust(len(token), '*')
        guild_name = guild_id  # Default if we can't get the name
        
        try:
            session = self.session_factory.create(token)
            guild_manager = GuildManager(session)
            
            # Try to get guild information
            guild_info = guild_manager.get_guild_info(guild_id)
            if guild_info:
                guild_name = guild_info.get("name", guild_id)
            
            # Modified: Direct bypass attempt without preliminary check
            success = False
            bypass_attempted = False
            
            # Try onboarding bypass
            try:
                onboarding_response = session.get(f"https://discord.com/api/v9/guilds/{guild_id}/onboarding")
                if onboarding_response.status_code == 200:
                    onboarding_data = onboarding_response.json()
                    if onboarding_data and onboarding_data.get("prompts"):
                        bypass_attempted = True
                        onboarding_success, error = self._complete_onboarding(session, guild_id, guild_name, onboarding_data)
                        if onboarding_success:
                            logger.info(f"Successfully completed onboarding for token {masked_token}")
                            self.stats["onboarding_bypassed"] += 1
                            success = True
                        else:
                            logger.warning(f"Failed to complete onboarding for token {masked_token}: {error}")
                            self._handle_error(guild_id, guild_name, error, masked_token)
            except Exception as e:
                logger.debug(f"Error during onboarding check/bypass: {str(e)}")
            
            # Try TOS bypass
            try:
                tos_response = session.get(
                    f"https://discord.com/api/v9/guilds/{guild_id}/member-verification",
                    params={'with_guild': 'false'}
                )
                if tos_response.status_code == 200:
                    tos_data = tos_response.json()
                    if tos_data and (tos_data.get('form_fields') or tos_data.get('description')):
                        bypass_attempted = True
                        tos_success, error = self._complete_tos_acceptance(session, guild_id, guild_name, tos_data)
                        if tos_success:
                            logger.info(f"Successfully accepted TOS for token {masked_token}")
                            self.stats["tos_accepted"] += 1
                            success = True
                        else:
                            logger.warning(f"Failed to accept TOS for token {masked_token}: {error}")
                            self._handle_error(guild_id, guild_name, error, masked_token)
            except Exception as e:
                logger.debug(f"Error during TOS check/bypass: {str(e)}")
            
            # If no bypass was attempted, likely already verified
            if not bypass_attempted:
                logger.info(f"No verification needed for token {masked_token} in guild {guild_name}")
                self.stats["already_verified"] += 1
                success = True
            
            return success, guild_name
                
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error processing token {masked_token}: {error_message}")
            return False, guild_name
    
    def _handle_error(self, guild_id: str, guild_name: str, error: str, token_hint: str) -> None:
        """Handle verification errors and update statistics"""
        if "Missing Access" in error or "access" in error.lower():
            self.stats["no_access"] += 1
            # Add to manual verification list
            if guild_id not in self.manual_verification_needed:
                self.manual_verification_needed[guild_id] = {
                    "name": guild_name,
                    "error": error,
                    "tokens": []
                }
            
            self.manual_verification_needed[guild_id]["tokens"].append(token_hint)
            ManualVerificationTracker.add_guild(guild_id, guild_name, error, token_hint)
        elif "phone verification" in error.lower():
            self.stats["phone_verification_required"] += 1
        else:
            self.stats["failed"] += 1
    
    def _complete_onboarding(self, session: tls_client.Session, guild_id: str, guild_name: str, 
                           data: Dict[str, Any]) -> Tuple[bool, str]:
        """Submit onboarding responses to Discord API with detailed error reporting"""
        try:
            payload = self._build_onboarding_payload(data)
            
            response = session.post(
                f"https://discord.com/api/v9/guilds/{guild_id}/onboarding-responses",
                json=payload
            )
            
            if response.status_code == 200:
                return True, ""
            elif response.status_code == 403:
                error_message = "Missing Access"
                try:
                    error_message = response.json().get("message", "Missing Access")
                except:
                    pass
                    
                return False, error_message
            elif response.status_code == 429:
                retry_after = 60
                try:
                    retry_after = int(response.json().get("retry_after", 60)) + 1
                except:
                    pass
                
                logger.warning(f"Rate limited when processing guild '{guild_name}'. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                
                # Try again after waiting
                response = session.post(
                    f"https://discord.com/api/v9/guilds/{guild_id}/onboarding-responses",
                    json=payload
                )
                
                if response.status_code == 200:
                    return True, ""
                else:
                    try:
                        error_message = response.json().get("message", f"HTTP error {response.status_code}")
                    except:
                        error_message = f"HTTP error {response.status_code}"
                    return False, error_message
            else:
                error_message = f"HTTP error {response.status_code}"
                try:
                    error_message = response.json().get("message", error_message)
                except:
                    pass
                
                return False, error_message
                
        except Exception as e:
            return False, str(e)
    
    def _complete_tos_acceptance(self, session: tls_client.Session, guild_id: str, guild_name: str, 
                               data: Dict[str, Any]) -> Tuple[bool, str]:
        """Submit TOS acceptance to Discord"""
        try:
            payload = {
                'form_fields': data.get('form_fields', None),
                'version': data.get('version', '2023-05-19'),
                'description': data.get('description', ''),
                'acknowledgement': True,
                'recommendation_id': None,
                'recommendation_context': 'GLOBAL_DISCOVERY_TOP_PICKS',
                'recommendation_outcome': 'UNKNOWN'
            }
            
            response = session.put(
                f"https://discord.com/api/v9/guilds/{guild_id}/requests/@me",
                json=payload
            )
            
            if response.status_code in [200, 201]:
                return True, ""
            elif response.status_code == 403:
                error_message = "Missing Access"
                try:
                    error_message = response.json().get("message", "Missing Access")
                except:
                    pass
                    
                return False, error_message
            elif response.status_code == 429:
                retry_after = 60
                try:
                    retry_after = int(response.json().get("retry_after", 60)) + 1
                except:
                    pass
                
                logger.warning(f"Rate limited when accepting TOS for '{guild_name}'. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                
                # Try again after waiting
                response = session.put(
                    f"https://discord.com/api/v9/guilds/{guild_id}/requests/@me",
                    json=payload
                )
                
                if response.status_code in [200, 201]:
                    return True, ""
                else:
                    try:
                        error_message = response.json().get("message", f"HTTP error {response.status_code}")
                    except:
                        error_message = f"HTTP error {response.status_code}"
                    return False, error_message
            else:
                error_message = f"HTTP error {response.status_code}"
                try:
                    error_message = response.json().get("message", error_message)
                except:
                    pass
                
                return False, error_message
                
        except Exception as e:
            return False, str(e)
    
    def _build_onboarding_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build the payload for onboarding response submission"""
        timestamp = int(datetime.now().timestamp())
        prompts = data.get("prompts", [])
        
        # Track all prompts seen
        prompts_seen = {prompt["id"]: timestamp for prompt in prompts}
        
        # Track all options seen
        options_seen = {}
        for prompt in prompts:
            for option in prompt.get("options", []):
                options_seen[option["id"]] = timestamp
        
        # Select options (for simplicity, selecting the last option from each prompt)
        selected_options = []
        for prompt in prompts:
            options = prompt.get("options", [])
            if options:
                # Select last option for each prompt
                selected_options.append(options[-1]["id"])
        
        return {
            "onboarding_responses": selected_options,
            "onboarding_prompts_seen": prompts_seen,
            "onboarding_responses_seen": options_seen
        }


def main():
    """Main entry point for the application"""
    print(BANNER)
    
    # Initialize configuration
    config = Config()
    if not config.load():
        print(f"{Fore.RED}Failed to load configuration or no tokens available. Exiting.{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}Select operation mode:{Style.RESET_ALL}")
    print(f"1. {Fore.GREEN}Auto-detect and bypass verification for all servers{Style.RESET_ALL}")
    print(f"2. {Fore.YELLOW}Bypass verification for a specific server (Guild ID){Style.RESET_ALL}")
    
    try:
        choice = input(f"{Fore.CYAN}Enter your choice (1/2): {Style.RESET_ALL}")
        
        bypass = VerificationBypass(config)
        
        if choice == '1':
            print(f"{Fore.GREEN}Starting automatic verification bypass for all servers...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}This will process {len(config.tokens)} tokens and apply delays only between servers needing verification{Style.RESET_ALL}")
            bypass.process_all_guilds()
            
        elif choice == '2':
            guild_id = input(f"{Fore.CYAN}Enter Discord Server/Guild ID: {Style.RESET_ALL}")
            if not guild_id or not guild_id.strip().isdigit():
                print(f"{Fore.RED}Invalid Guild ID. Exiting.{Style.RESET_ALL}")
                return
            
            bypass.bypass_for_guild(guild_id.strip())
            
        else:
            print(f"{Fore.RED}Invalid choice. Exiting.{Style.RESET_ALL}")
            return
            
        # Show stats summary
        print(f"\n{Fore.CYAN}===== Verification Stats ====={Style.RESET_ALL}")
        print(f"{Fore.GREEN}Onboarding Bypassed: {bypass.stats['onboarding_bypassed']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}TOS Accepted: {bypass.stats['tos_accepted']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Already Verified: {bypass.stats['already_verified']}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed: {bypass.stats['failed']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}No Access: {bypass.stats['no_access']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Phone Verification Required: {bypass.stats['phone_verification_required']}{Style.RESET_ALL}")
        
        # Show summary of manual verification needed
        if bypass.manual_verification_needed:
            print(f"\n{Fore.YELLOW}=== Servers Requiring Manual Verification ==={Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{len(bypass.manual_verification_needed)} servers need manual verification.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Details saved to:{Style.RESET_ALL} {Fore.CYAN}manual_verification_needed.txt{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Summary saved to:{Style.RESET_ALL} {Fore.CYAN}verification_summary.txt{Style.RESET_ALL}")
            
        print(f"\n{Fore.GREEN}Verification bypass completed!{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Process interrupted by user. Exiting.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Critical error occurred: {str(e)}{Style.RESET_ALL}")
        logger.exception("Critical error")


if __name__ == "__main__":
    main()