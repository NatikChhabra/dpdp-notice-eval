# Free Spaces run on ZeroGPU, which needs at least one @spaces.GPU function to start.
# This app doesn't use a GPU, so this placeholder is never called.
import spaces

from dpdp_eval.web import main


@spaces.GPU
def _gpu_placeholder(): return None


main()
