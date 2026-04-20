"""
utils/refactor_doc_links.py

Deterministic repair utility to patch broken internal markdown links resulting
from the Institutional Memory YYYY-MM-DD prefix timestamping execution.
"""
import os
import re
import glob

# Hardcoded source of truth derived from the bash timestamping stdout payload
RENAME_MAP = {
    "enterprise_orchestration_vision_2027.md": "2026-03-26_enterprise_orchestration_vision_2027.md",
    "variant_annotation_optimizations.md": "2026-03-19_variant_annotation_optimizations.md",
    "phase_14_hybrid_orchestration.md": "2026-03-26_phase_14_hybrid_orchestration.md",
    "phase_148_tech_debt_and_optimization.md": "2026-03-30_phase_148_tech_debt_and_optimization.md",
    "scatter-gather-bam-merging.md": "2026-03-25_scatter-gather-bam-merging.md",
    "phase_11_strategic_roadmap.md": "2026-03-18_phase_11_strategic_roadmap.md",
    "red_team_roadmap.md": "2026-03-30_red_team_roadmap.md",
    "phase_20_finops_ai_roadmap.md": "2026-03-19_phase_20_finops_ai_roadmap.md",
    "phase28_somatic_paired_workflow.md": "2026-03-19_phase28_somatic_paired_workflow.md",
    "SARS_CoV_2_ROADMAP.md": "2026-03-24_SARS_CoV_2_ROADMAP.md",
    "phase_146_context_health_monitor.md": "2026-03-29_phase_146_context_health_monitor.md",
    "phase_147_infrastructure_resiliency.md": "2026-03-30_phase_147_infrastructure_resiliency.md",
    "deepsomatic-case-study-wgs.md": "2026-03-26_deepsomatic-case-study-wgs.md",
    "deepsomatic-case-study-ont.md": "2026-03-26_deepsomatic-case-study-ont.md",
    "deepsomatic-case-study-wes.md": "2026-03-26_deepsomatic-case-study-wes.md",
    "deepsomatic-case-study-ffpe-wgs-tumor-only.md": "2026-03-26_deepsomatic-case-study-ffpe-wgs-tumor-only.md",
    "deepsomatic-case-study-ont-tumor-only.md": "2026-03-26_deepsomatic-case-study-ont-tumor-only.md",
    "deepsomatic-case-study-ffpe-wes-tumor-only.md": "2026-03-26_deepsomatic-case-study-ffpe-wes-tumor-only.md",
    "README.md": "2026-03-26_README.md",
    "deepsomatic-quick-start.md": "2026-03-26_deepsomatic-quick-start.md",
    "deepsomatic-case-study-wgs-tumor-only.md": "2026-03-26_deepsomatic-case-study-wgs-tumor-only.md",
    "deepsomatic-case-study-ffpe-wgs.md": "2026-03-26_deepsomatic-case-study-ffpe-wgs.md",
    "deepsomatic-case-study-pacbio-tumor-only.md": "2026-03-26_deepsomatic-case-study-pacbio-tumor-only.md",
    "deepsomatic-case-study-pacbio.md": "2026-03-26_deepsomatic-case-study-pacbio.md",
    "deepsomatic-case-study-ffpe-wes.md": "2026-03-26_deepsomatic-case-study-ffpe-wes.md",
    "metrics.md": "2026-03-26_metrics.md",
    "deepsomatic-case-study-wes-tumor-only.md": "2026-03-26_deepsomatic-case-study-wes-tumor-only.md",
    "deepsomatic-hybrid-pacbio-illumina.md": "2026-03-26_deepsomatic-hybrid-pacbio-illumina.md",
    "mar24_walkthrough_issue4_phase3.md": "2026-03-25_mar24_walkthrough_issue4_phase3.md",
    "mar24_implementation_plan_issue3_phase1.md": "2026-03-25_mar24_implementation_plan_issue3_phase1.md",
    "implementation_plan_sprint5_issue1.md": "2026-03-25_implementation_plan_sprint5_issue1.md",
    "walkthrough_sprint4_issue3.md": "2026-03-25_walkthrough_sprint4_issue3.md",
    "db_tunnel_sync_implementation_plan.md": "2026-03-25_db_tunnel_sync_implementation_plan.md",
    "implementation_plan_sprint3_issue4.md": "2026-03-25_implementation_plan_sprint3_issue4.md",
    "implementation_plan_sprint5_issue4.md": "2026-03-25_implementation_plan_sprint5_issue4.md",
    "implementation_plan_sprint3_issue1.md": "2026-03-25_implementation_plan_sprint3_issue1.md",
    "mar24_walkthrough_issue2_phase3.md": "2026-03-25_mar24_walkthrough_issue2_phase3.md",
    "mar27_fresh_walkthrough.md": "2026-03-27_mar27_fresh_walkthrough.md",
    "mar24_walkthrough_sprint2_issue2.md": "2026-03-25_mar24_walkthrough_sprint2_issue2.md",
    "walkthrough_sprint2_issue3.md": "2026-03-25_walkthrough_sprint2_issue3.md",
    "mar24_phase3_walkthrough.md": "2026-03-25_mar24_phase3_walkthrough.md",
    "walkthrough_sprint4_issue2.md": "2026-03-25_walkthrough_sprint4_issue2.md",
    "s3_cleanup_implementation_plan.md": "2026-03-28_s3_cleanup_implementation_plan.md",
    "mar24_newphase1_implementation_plan.md": "2026-03-25_mar24_newphase1_implementation_plan.md",
    "mar24_implementation_plan_issue2.md": "2026-03-25_mar24_implementation_plan_issue2.md",
    "merge_bams_implementation_plan.md": "2026-03-29_merge_bams_implementation_plan.md",
    "walkthrough_sprint5_issue3.md": "2026-03-25_walkthrough_sprint5_issue3.md",
    "hybrid_head_node_implementation_plan.md": "2026-03-26_hybrid_head_node_implementation_plan.md",
    "mar24_implementation_plan_sprint2_issue2.md": "2026-03-25_mar24_implementation_plan_sprint2_issue2.md",
    "implementation_plan_sprint4_issue1.md": "2026-03-25_implementation_plan_sprint4_issue1.md",
    "implementation_plan_sprint4_issue5.md": "2026-03-25_implementation_plan_sprint4_issue5.md",
    "walkthrough_sprint3_issue2.md": "2026-03-25_walkthrough_sprint3_issue2.md",
    "implementation_plan_sprint4_issue4.md": "2026-03-25_implementation_plan_sprint4_issue4.md",
    "walkthrough_sprint3_issue3.md": "2026-03-25_walkthrough_sprint3_issue3.md",
    "mar24_walkthrough_issue3_phase3.md": "2026-03-25_mar24_walkthrough_issue3_phase3.md",
    "walkthrough_sprint5_issue2.md": "2026-03-25_walkthrough_sprint5_issue2.md",
    "phase142_implementation_plan.md": "2026-03-28_phase142_implementation_plan.md",
    "phase112_walkthrough.md": "2026-03-25_phase112_walkthrough.md",
    "revised_merge_bams_implementation_plan.md": "2026-03-29_revised_merge_bams_implementation_plan.md",
    "walkthrough_sprint5_issue1.md": "2026-03-25_walkthrough_sprint5_issue1.md",
    "sra_to_fastq_enospc_implementation_plan.md": "2026-03-26_sra_to_fastq_enospc_implementation_plan.md",
    "phase108_walkthrough.md": "2026-03-25_phase108_walkthrough.md",
    "implementation_plan_sprint4_issue3.md": "2026-03-25_implementation_plan_sprint4_issue3.md",
    "mar27_fresh_implementation_plan.md": "2026-03-27_mar27_fresh_implementation_plan.md",
    "walkthrough_sprint3_issue4.md": "2026-03-25_walkthrough_sprint3_issue4.md",
    "implementation_plan_sprint4_issue2.md": "2026-03-25_implementation_plan_sprint4_issue2.md",
    "walkthrough_sprint5_issue4.md": "2026-03-25_walkthrough_sprint5_issue4.md",
    "walkthrough_sprint3_issue1.md": "2026-03-25_walkthrough_sprint3_issue1.md",
    "implementation_plan_sprint2_issue3.md": "2026-03-25_implementation_plan_sprint2_issue3.md",
    "implementation_plan_scatter_gather.md": "2026-03-25_implementation_plan_scatter_gather.md",
    "phase111_walkthrough.md": "2026-03-25_phase111_walkthrough.md",
    "walkthrough_sprint4_issue5.md": "2026-03-25_walkthrough_sprint4_issue5.md",
    "mar26_monumental_walkthrough.md": "2026-03-26_mar26_monumental_walkthrough.md",
    "implementation_plan_sprint3_issue2.md": "2026-03-25_implementation_plan_sprint3_issue2.md",
    "implementation_plan_sprint5_issue3.md": "2026-03-25_implementation_plan_sprint5_issue3.md",
    "walkthrough_sprint4_issue1.md": "2026-03-25_walkthrough_sprint4_issue1.md",
    "implementation_plan_sprint5_issue2.md": "2026-03-25_implementation_plan_sprint5_issue2.md",
    "walkthrough_sprint4_issue4.md": "2026-03-25_walkthrough_sprint4_issue4.md",
    "mar24_walkthrough_sprint2_issue1_phase3.md": "2026-03-25_mar24_walkthrough_sprint2_issue1_phase3.md",
    "implementation_plan_sprint3_issue3.md": "2026-03-25_implementation_plan_sprint3_issue3.md",
    "mar24_implementation_plan_issue4.md": "2026-03-25_mar24_implementation_plan_issue4.md",
    "phase_19_finops_billing_audit.md": "2026-03-19_phase_19_finops_billing_audit.md",
    "sprint_2_tunnel_synchronization.md": "2026-03-24_sprint_2_tunnel_synchronization.md",
    "phase_16_17_ssm_database_roles.md": "2026-03-19_phase_16_17_ssm_database_roles.md",
    "phase_30_33_intelligent_routing_and_probing.md": "2026-03-20_phase_30_33_intelligent_routing_and_probing.md",
    "phase_58_to_71_cloud_egress_and_validation.md": "2026-03-22_phase_58_to_71_cloud_egress_and_validation.md",
    "phase_37_38_sovereign_finops.md": "2026-03-21_phase_37_38_sovereign_finops.md",
    "phase26_byoc_wrapper.md": "2026-03-19_phase26_byoc_wrapper.md",
    "phase_42_aws_diagnostic_triage.md": "2026-03-22_phase_42_aws_diagnostic_triage.md",
    "phase_12_s3_telemetry_polling.md": "2026-03-18_phase_12_s3_telemetry_polling.md",
    "phase_13_gpu_alignment.md": "2026-03-18_phase_13_gpu_alignment.md",
    "run_seqc2_network_sever.md": "2026-03-26_run_seqc2_network_sever.md",
    "phase_15_telemetry_webhooks.md": "2026-03-18_phase_15_telemetry_webhooks.md",
    "phase_6_auth0_react.md": "2026-03-18_phase_6_auth0_react.md",
    "phase_21_vep_integration.md": "2026-03-19_phase_21_vep_integration.md",
    "phase_8_orchestration_visuals.md": "2026-03-18_phase_8_orchestration_visuals.md",
    "phase_86_to_88_autonomous_finops_profiler.md": "2026-03-24_phase_86_to_88_autonomous_finops_profiler.md",
    "phase_143_sra_ebs_buffering_and_act.md": "2026-03-28_phase_143_sra_ebs_buffering_and_act.md",
    "phase_14_finops_analytics.md": "2026-03-18_phase_14_finops_analytics.md",
    "phase_144_real_time_microbilling.md": "2026-03-28_phase_144_real_time_microbilling.md",
    "phase29_finops_architect.md": "2026-03-20_phase29_finops_architect.md",
    "phase_75_to_83_ui_egress_and_cache_poisoning.md": "2026-03-24_phase_75_to_83_ui_egress_and_cache_poisoning.md",
    "phase_73_to_74_telemetry_race_condition_and_ci_cd.md": "2026-03-22_phase_73_to_74_telemetry_race_condition_and_ci_cd.md",
    "phase_26_spot_arbitrage.md": "2026-03-19_phase_26_spot_arbitrage.md",
    "phase26_retrospective.md": "2026-03-19_phase26_retrospective.md",
    "phase_4_enterprise_hardening.md": "2026-03-24_phase_4_enterprise_hardening.md",
    "phase_43_to_55_architecture_consolidation.md": "2026-03-22_phase_43_to_55_architecture_consolidation.md",
    "phase_18_orchestration_resilience.md": "2026-03-19_phase_18_orchestration_resilience.md",
    "phase_30_intelligent_routing.md": "2026-03-20_phase_30_intelligent_routing.md",
    "phase_20_enterprise_alignment.md": "2026-03-19_phase_20_enterprise_alignment.md",
    "phase_107_to_112_somatic_scatter_and_sra_stabilization.md": "2026-03-24_phase_107_to_112_somatic_scatter_and_sra_stabilization.md",
    "phase_85_engineering_meta_analysis.md": "2026-03-24_phase_85_engineering_meta_analysis.md",
    "phase_35_great_scrub.md": "2026-03-21_phase_35_great_scrub.md",
    "phase_89_to_106_viral_orchestration_stabilization.md": "2026-03-24_phase_89_to_106_viral_orchestration_stabilization.md",
    "phase-40-41-telemetry-decoupling.md": "2026-03-21_phase-40-41-telemetry-decoupling.md",
    "phase_142_modular_entrypoints.md": "2026-03-28_phase_142_modular_entrypoints.md",
    "phase22_retrospective.md": "2026-03-19_phase22_retrospective.md",
    "phase1_somatic_infrastructure_victory.md": "2026-03-26_phase1_somatic_infrastructure_victory.md",
    "phase_113_to_124_orchestration_hard_armor.md": "2026-03-27_phase_113_to_124_orchestration_hard_armor.md"
}

def parse_and_preview_markdown_links(target_dir="docs"):
    """
    Standard pass: Fixes markdown URL paths e.g. [Link Text](../phase_X.md)
    """
    matched_files = [
        os.path.join(dp, f) 
        for dp, dn, filenames in os.walk(target_dir) 
        for f in filenames if f.endswith('.md')
    ]
    
    link_pattern = re.compile(r"(\[[^\]]+\]\()([^\)]+)(\))")
    total_modifications = 0
    
    for filepath in matched_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            continue
            
        changes_in_file = 0
        def replacement_evaluator(match):
            nonlocal changes_in_file
            prefix, url, suffix = match.groups()
            
            if url.startswith("http://") or url.startswith("https://") or url.startswith("mailto:"):
                return match.group(0)
                
            original_basename = os.path.basename(url)
            
            if "#" in original_basename:
                filename_part = original_basename.split("#")[0]
                hash_part = "#" + original_basename.split("#", 1)[1]
            else:
                filename_part = original_basename
                hash_part = ""
            
            if filename_part in RENAME_MAP:
                new_basename = RENAME_MAP[filename_part] + hash_part
                new_url = url.replace(original_basename, new_basename)
                changes_in_file += 1
                return f"{prefix}{new_url}{suffix}"
            
            return match.group(0)
        
        new_content = link_pattern.sub(replacement_evaluator, content)
        if changes_in_file > 0:
            total_modifications += changes_in_file
            # with open(filepath, 'w', encoding='utf-8') as f:
            #     f.write(new_content)
    return total_modifications

def parse_and_preview_raw_references(target_dirs=["docs/architecture", "docs/gemini"]):
    """
    Secondary pass: Finds raw broken text references (e.g. `docs/retrospectives/phase_6.md`)
    that exist openly in the code blocks, text descriptions, or lists in specified folders.
    Uses negative lookbehind to ensure we don't accidentally double-prefix.
    """
    matched_files = []
    for d in target_dirs:
        matched_files.extend([
            os.path.join(dp, f) 
            for dp, dn, filenames in os.walk(d) 
            for f in filenames if f.endswith('.md')
        ])
        
    print(f"🔍 Discovered {len(matched_files)} '.md' files in {target_dirs} for raw text inspection.\n")
    total_modifications = 0
    
    for filepath in matched_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            continue
            
        changes_in_file = 0
        new_content = content
        
        for old_file, new_file in RENAME_MAP.items():
            # Match old_file only if it's NOT already preceded by a YYYY-MM-DD_ prefix.
            # We use a negative lookbehind for an underscore, since the prefix is [0-9]{4}..._
            pattern = re.compile(r'(?<![0-9]{4}-[0-9]{2}-[0-9]{2}_)' + re.escape(old_file))
            
            # Check if there's any match
            matches = pattern.findall(new_content)
            if matches:
                changes_in_file += len(matches)
                print(f"    🔄 {filepath}: Mutating raw text reference [{old_file}] -> [{new_file}] ({len(matches)} occurrences)")
                new_content = pattern.sub(new_file, new_content)
                
        if changes_in_file > 0:
            total_modifications += changes_in_file
            # ⬇️ UNCOMMENT BELOW BLOCK FOR PRODUCTION DEPLOYMENT ⬇️
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
    print(f"\n✅ Raw Text Execution Complete. Simulated {total_modifications} raw string state mutations.")

if __name__ == "__main__":
    parse_and_preview_markdown_links("docs")
    parse_and_preview_raw_references(["docs/architecture", "docs/gemini"])
