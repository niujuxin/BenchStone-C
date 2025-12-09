
from pathlib import Path
import sys


REPO_ABSOLUTE_BASE = Path('/home/niujuxin/bighls/metabench_repos')

class RepoPaths:
    TheAlgorithms_C = 'algorithm_c'
    DaveGamble_cJSON = 'cJSON'
    curl = 'curl'
    FreeRTOS_Kernel = 'FreeRTOS-Kernel'
    git = 'git'
    ampl_gsl = 'gsl'
    jq = 'jq'
    lua = 'lua'
    lz4 = 'lz4'
    Mbed_TLS_mbedtls = 'mbedtls'
    netdata = 'netdata'
    openssl = 'openssl'
    h2o_picohttpparser = 'picohttpparser'
    redis = 'redis'
    scrcpy = 'scrcpy'
    sqlite = 'sqlite'
    nothings_stb = 'stb'
    leethomason_tinyxml2 = 'tinyxml2'
    martanne_vis = 'vis'
    facebook_zstd = 'zstd'

    @classmethod
    def iter_repos(cls):
        for attr in dir(cls):
            if attr.startswith('_'):
                continue
            val = getattr(cls, attr)
            if not isinstance(val, str):
                continue
            repo_path = REPO_ABSOLUTE_BASE / val
            yield (attr, repo_path)


if __name__ == '__main__':
    # Check if all repos exists.
    missing = []
    for repo_name, repo_path in RepoPaths.iter_repos():
        if not repo_path.exists():
            missing.append((repo_name, repo_path))

    if not missing:
        print(f"All repositories exist under {REPO_ABSOLUTE_BASE}")
        sys.exit(0)

    print("Missing repositories:")
    for name, path in missing:
        print(f" - {name!r} -> {path}")
    sys.exit(1)
