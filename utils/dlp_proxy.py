import re

def redact_genomic_phi(content: str, redact_uuids: bool = True) -> str:
    """
    Pass payload through DLP Regex Proxies statically.
    
    Args:
        content (str): The raw string payload to scrub.
        redact_uuids (bool): If True, strips AWS/Terraform/Auth0 UUID mappings. 
                             Set to False ONLY within bounded infrastructure diagnostic tools.
    """
    if not isinstance(content, str):
        return content

    # Example of how to add a new DLP regex proxy
    # Redact Genomic sequence
    content = re.sub(r'[ATCGatcg]{20,}', '<REDACTED_PHI>', content)
    
    # Redact VCF coordinates (chrX:12345-67890 or 1:12345) structurally matching the Go firewall
    vcf_pattern = r'(?i)(?<!\.)\bchr(?:[1-9]|1[0-9]|2[0-2]|X|Y|M):\d{1,9}(?:-\d{1,9})?\b|^(?:chr)?(?:[1-9]|1[0-9]|2[0-2]|X|Y|M)\t\d{1,9}\t|(?<!\.)\b(?:[1-9]|1[0-9]|2[0-2]|X|Y|M):\d{4,9}(?:-\d{1,9})?\b'
    content = re.sub(vcf_pattern, '<REDACTED_PHI>', content, flags=re.MULTILINE)
    
    if redact_uuids:
        # Whitelist: Preserve ADK session IDs that are explicitly labeled as sessions.
        # Matches patterns like "session_id: <uuid>", "Session ID: <uuid>", "session/<uuid>",
        # "session=<uuid>", or "adk-session:<uuid>" to allow cross-session trace referencing.
        _uuid = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
        _session_ctx = re.compile(
            rf'((?:session[_\s]?id\s*[:=]\s*|session/|adk[_-]session\s*[:=]\s*|Session\s+ID\s*[:=]\s*))({_uuid})',
            re.IGNORECASE
        )
        # Extract and protect session-context UUIDs with sentinel tokens
        session_refs = {}
        def _protect(m):
            sentinel = f'__ADK_SESSION_{len(session_refs)}__'
            session_refs[sentinel] = m.group(0)
            return sentinel
        content = _session_ctx.sub(_protect, content)
        
        # Redact all remaining UUIDs structurally
        content = re.sub(_uuid, '<REDACTED_PHI>', content)
        
        # Restore protected ADK session references
        for sentinel, original in session_refs.items():
            content = content.replace(sentinel, original)
        
    return content
