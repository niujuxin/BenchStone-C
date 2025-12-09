
import logging
from pathlib import Path

from dependency_resolve_kernel import search
from src.all_repos import REPO_ABSOLUTE_BASE, RepoPaths
from src.crepo import CRepo
from src.csource.csource import CSource
from src.design_construct.schema_config import DesignMetaV2
from src.design_construct.schema_trace import DesignConstructTrace
from src.utils.misc import dump_json, read_json, read_jsonl


# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    import argparse

    VERBOSE = True

    parser = argparse.ArgumentParser(
        description="Construct designs for horizontal kernels."
    )
    parser.add_argument('--repo', type=str, required=True)
    parser.add_argument('--granularity', type=str, 
                        choices=['primitive', 'routine', 'workflow', 'end_to_end_scenario'],
                        nargs='+', # Allow multiple values
                        required=True)
    args = parser.parse_args()

    supported_repos = [name for name, _ in RepoPaths.iter_repos()]
    if args.repo not in supported_repos:
        raise ValueError(
            f"Unsupported repo name {args.repo!r}. "
            f"Supported repos: {supported_repos}"
        )
    
    REPO_NAME: str = RepoPaths.__dict__[args.repo]
    REPO_ROOT = REPO_ABSOLUTE_BASE / REPO_NAME

    META_INFO_SAVE_PATH = Path('./kernels/category/') / f"{REPO_NAME}.jsonl"
    if META_INFO_SAVE_PATH.exists():
        designs = read_jsonl(META_INFO_SAVE_PATH)
    else:
        raise FileNotFoundError(f"Meta info file {META_INFO_SAVE_PATH} not found.")

    DESIGN_OVERWRITE = False
    DESIGN_META_SAVE_NAME = 'meta.json'
    DESIGN_TRACE_SAVE_NAME = 'trace.json'

    DESIGN_SAVE_BASE = Path("/home/niujuxin/MetaBench-C-Dataset/v2/") / REPO_NAME
    DESIGN_SAVE_BASE.mkdir(parents=True, exist_ok=True)
    logger.info(f"Designs will be saved to {DESIGN_SAVE_BASE}")

    repo = CRepo(REPO_ROOT)

    csource_dict: dict[Path, CSource] = {}
    for fp in repo.files():
        rel_fp = fp.relative_to(REPO_ABSOLUTE_BASE)
        csource_dict[rel_fp] = CSource.from_file(fp)

    suitable_designs = [d for d in designs if d.get('suitable', False) is True]

    selected_designs = []

    if 'primitive' in args.granularity:
        selected_designs.extend([d for d in suitable_designs if d.get('granularity', '') == 'primitive'])
    if 'routine' in args.granularity:
        selected_designs.extend([d for d in suitable_designs if d.get('granularity', '') == 'routine'])
    if 'workflow' in args.granularity:
        selected_designs.extend([d for d in suitable_designs if d.get('granularity', '') == 'workflow'])
    if 'end_to_end_scenario' in args.granularity:
        selected_designs.extend([d for d in suitable_designs if d.get('granularity', '') == 'end_to_end_scenario'])

    logger.info(f"Found {len(selected_designs)} designs to process in repo {REPO_NAME} "
                f"with granularity {args.granularity}.")

    for design in selected_designs:
        design_meta = DesignMetaV2(
            function_location=Path(design['file_path']),
            function_name=design['function_name'],
            logic_type=design['type'],
            granularity=design['granularity'],
        )

        final_part = design_meta.function_location.parts[-1]
        design_loc = DESIGN_SAVE_BASE / f"{design_meta.function_name}__{Path(final_part).stem}"

        if DESIGN_OVERWRITE:
            trace = DesignConstructTrace()
        else:
            trace_path = design_loc / DESIGN_TRACE_SAVE_NAME
            if trace_path.exists():
                VERBOSE and logger.info(f"Loading existing design trace from {trace_path}")
                trace = DesignConstructTrace.from_json(
                    read_json(trace_path)
                )
            else:
                VERBOSE and logger.info(f"No existing trace found at {trace_path}, "
                      f"starting new trace.")
                trace = DesignConstructTrace()
        
        try:

            for parent_uid, step in search(
                design_meta,
                list(trace.sequential_valid_step_iter()),
                csource_dict=csource_dict,
                max_iter=8,
                max_trace_steps=16,
                immed_dump_c_to=design_loc / 'design.c',
                immed_dump_h_to=design_loc / 'design.h',
                llm_version='deepseek-reasoner',
                verbose=VERBOSE,
            ):
                trace.add_new_step(step, parent_uid=parent_uid)
                dump_json(
                    trace.to_json(),
                    design_loc / DESIGN_TRACE_SAVE_NAME
                )
        
        except Exception as e:
            logger.error(f"Error processing design {design_meta.function_name} at "
                         f"{design_meta.function_location}: {e}")
            continue
