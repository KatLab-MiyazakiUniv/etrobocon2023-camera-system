# YOLOv5 🚀 by Ultralytics, AGPL-3.0 license
"""
PyTorch utils
"""

import math
import os
import platform
import subprocess
import time
import warnings
from contextlib import contextmanager
from copy import deepcopy
# from pathlib import Path

import torch
import torch.distributed as dist
import torch.nn as nn
import torch.nn.functional as F
# from torch.nn.parallel import DistributedDataParallel as DDP

from utils.general import check_version
# from utils.general import LOGGER, check_version, colorstr, file_date, git_describe

# https://pytorch.org/docs/stable/elastic/run.html
LOCAL_RANK = int(os.getenv('LOCAL_RANK', -1))
RANK = int(os.getenv('RANK', -1))
WORLD_SIZE = int(os.getenv('WORLD_SIZE', 1))

try:
    import thop  # for FLOPs computation
except ImportError:
    thop = None

# Suppress PyTorch warnings
warnings.filterwarnings(
    'ignore', message='User provided device_type of \'cuda\', but CUDA is not available. Disabling')
warnings.filterwarnings('ignore', category=UserWarning)


def smart_inference_mode(torch_1_9=check_version(torch.__version__, '1.9.0')):  # 必要
    # Applies torch.inference_mode() decorator if torch>=1.9.0 else torch.no_grad() decorator
    def decorate(fn):
        return (torch.inference_mode if torch_1_9 else torch.no_grad)()(fn)

    return decorate


@contextmanager
def torch_distributed_zero_first(local_rank: int):  # 必要
    # Decorator to make all processes in distributed training wait for each local_master to do something
    if local_rank not in [-1, 0]:
        dist.barrier(device_ids=[local_rank])
    yield
    if local_rank == 0:
        dist.barrier(device_ids=[0])


def device_count():  # 必要
    # Returns number of CUDA devices available. Safe version of torch.cuda.device_count(). Supports Linux and Windows
    assert platform.system() in (
        'Linux', 'Windows'), 'device_count() only supported on Linux or Windows'
    try:
        cmd = 'nvidia-smi -L | wc -l' if platform.system() == 'Linux' else 'nvidia-smi -L | find /c /v ""'  # Windows
        return int(subprocess.run(cmd, shell=True, capture_output=True, check=True).stdout.decode().split()[-1])
    except Exception:
        return 0


def select_device(device='', batch_size=0, newline=True):  # 必要
    # device = None or 'cpu' or 0 or '0' or '0,1,2,3'
    # s = f'YOLOv5 🚀 {git_describe() or file_date()} Python-{platform.python_version()} torch-{torch.__version__} '
    device = str(device).strip().lower().replace(
        'cuda:', '').replace('none', '')  # to string, 'cuda:0' to '0'
    cpu = device == 'cpu'
    mps = device == 'mps'  # Apple Metal Performance Shaders (MPS)
    if cpu or mps:
        # force torch.cuda.is_available() = False
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    elif device:  # non-cpu device requested
        # set environment variable - must be before assert is_available()
        os.environ['CUDA_VISIBLE_DEVICES'] = device
        assert torch.cuda.is_available() and torch.cuda.device_count() >= len(device.replace(',', '')), \
            f"Invalid CUDA '--device {device}' requested, use '--device cpu' or pass valid CUDA device(s)"

    if not cpu and not mps and torch.cuda.is_available():  # prefer GPU if available
        # range(torch.cuda.device_count())  # i.e. 0,1,6,7
        # devices = device.split(',') if device else '0'
        # n = len(devices)  # device count
        # if n > 1 and batch_size > 0:  # check batch_size is divisible by device_count
        #     assert batch_size % n == 0, f'batch-size {batch_size} not multiple of GPU count {n}'
        # space = ' ' * (len(s) + 1)
        # for i, d in enumerate(devices):
        #     p = torch.cuda.get_device_properties(i)
        #     bytes to MB
        #     s += f"{'' if i == 0 else space}CUDA:{d} ({p.name}, {p.total_memory / (1 << 20):.0f}MiB)\n"
        arg = 'cuda:0'
    # prefer MPS if available
    elif mps and getattr(torch, 'has_mps', False) and torch.backends.mps.is_available():
        s += 'MPS\n'
        arg = 'mps'
    else:  # revert to CPU
        # s += 'CPU\n'
        arg = 'cpu'

    # if not newline:
    #     s = s.rstrip()
    # LOGGER.info(s)
    return torch.device(arg)

def time_sync():
    # PyTorch-accurate time
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    return time.time()


def profile(input, ops, n=10, device=None): # 使わない
    """ YOLOv5 speed/memory/FLOPs profiler
    Usage:
        input = torch.randn(16, 3, 640, 640)
        m1 = lambda x: x * torch.sigmoid(x)
        m2 = nn.SiLU()
        profile(input, [m1, m2], n=100)  # profile over 100 iterations
    """
    results = []
    # if not isinstance(device, torch.device):
    #     device = select_device(device)
    # print(f"{'Params':>12s}{'GFLOPs':>12s}{'GPU_mem (GB)':>14s}{'forward (ms)':>14s}{'backward (ms)':>14s}"
    #       f"{'input':>24s}{'output':>24s}")

    # for x in input if isinstance(input, list) else [input]:
    #     x = x.to(device)
    #     x.requires_grad = True
    #     for m in ops if isinstance(ops, list) else [ops]:
    #         m = m.to(device) if hasattr(m, 'to') else m  # device
    #         m = m.half() if hasattr(m, 'half') and isinstance(
    #             x, torch.Tensor) and x.dtype is torch.float16 else m
    #         tf, tb, t = 0, 0, [0, 0, 0]  # dt forward, backward
    #         try:
    #             flops = thop.profile(m, inputs=(x, ), verbose=False)[
    #                 0] / 1E9 * 2  # GFLOPs
    #         except Exception:
    #             flops = 0

    #         try:
    #             for _ in range(n):
    #                 t[0] = time_sync()
    #                 y = m(x)
    #                 t[1] = time_sync()
    #                 try:
    #                     _ = (sum(yi.sum() for yi in y) if isinstance(
    #                         y, list) else y).sum().backward()
    #                     t[2] = time_sync()
    #                 except Exception:  # no backward method
    #                     # print(e)  # for debug
    #                     t[2] = float('nan')
    #                 tf += (t[1] - t[0]) * 1000 / n  # ms per op forward
    #                 tb += (t[2] - t[1]) * 1000 / n  # ms per op backward
    #             mem = torch.cuda.memory_reserved() / 1E9 if torch.cuda.is_available() else 0  # (GB)
    #             s_in, s_out = (tuple(x.shape) if isinstance(
    #                 x, torch.Tensor) else 'list' for x in (x, y))  # shapes
    #             p = sum(x.numel() for x in m.parameters()) if isinstance(
    #                 m, nn.Module) else 0  # parameters
    #             print(
    #                 f'{p:12}{flops:12.4g}{mem:>14.3f}{tf:14.4g}{tb:14.4g}{str(s_in):>24s}{str(s_out):>24s}')
    #             results.append([p, flops, mem, tf, tb, s_in, s_out])
    #         except Exception as e:
    #             print(e)
    #             results.append(None)
    #         torch.cuda.empty_cache()
    return results

"""
def is_parallel(model):
    # Returns True if model is of type DP or DDP
    return type(model) in (nn.parallel.DataParallel, nn.parallel.DistributedDataParallel)


def de_parallel(model):
    # De-parallelize a model: returns single-GPU model if model is of type DP or DDP
    return model.module if is_parallel(model) else model
# """


def initialize_weights(model): # 必要
    for m in model.modules():
        t = type(m)
        if t is nn.Conv2d:
            # nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            pass
        elif t is nn.BatchNorm2d:
            m.eps = 1e-3
            m.momentum = 0.03
        elif t in [nn.Hardswish, nn.LeakyReLU, nn.ReLU, nn.ReLU6, nn.SiLU]:
            m.inplace = True

"""
def sparsity(model):
    # Return global model sparsity
    a, b = 0, 0
    for p in model.parameters():
        a += p.numel()
        b += (p == 0).sum()
    return b / a
"""


# def prune(model, amount=0.3):
#     # Prune model to requested global sparsity
#     import torch.nn.utils.prune as prune
#     for name, m in model.named_modules():
#         if isinstance(m, nn.Conv2d):
#             prune.l1_unstructured(m, name='weight', amount=amount)  # prune
#             prune.remove(m, 'weight')  # make permanent
#     LOGGER.info(f'Model pruned to {sparsity(model):.3g} global sparsity')


def fuse_conv_and_bn(conv, bn): # 必要
    # Fuse Conv2d() and BatchNorm2d() layers https://tehnokv.com/posts/fusing-batchnorm-and-conv/
    fusedconv = nn.Conv2d(conv.in_channels,
                          conv.out_channels,
                          kernel_size=conv.kernel_size,
                          stride=conv.stride,
                          padding=conv.padding,
                          dilation=conv.dilation,
                          groups=conv.groups,
                          bias=True).requires_grad_(False).to(conv.weight.device)

    # Prepare filters
    w_conv = conv.weight.clone().view(conv.out_channels, -1)
    w_bn = torch.diag(bn.weight.div(torch.sqrt(bn.eps + bn.running_var)))
    fusedconv.weight.copy_(torch.mm(w_bn, w_conv).view(fusedconv.weight.shape))

    # Prepare spatial bias
    b_conv = torch.zeros(conv.weight.size(
        0), device=conv.weight.device) if conv.bias is None else conv.bias
    b_bn = bn.bias - \
        bn.weight.mul(bn.running_mean).div(torch.sqrt(bn.running_var + bn.eps))
    fusedconv.bias.copy_(
        torch.mm(w_bn, b_conv.reshape(-1, 1)).reshape(-1) + b_bn)

    return fusedconv


def model_info(model, verbose=False, imgsz=640):
    pass
    """
    Model information. img_size may be int or list, i.e. img_size=640 or img_size=[640, 320]
    n_p = sum(x.numel() for x in model.parameters())  # number parameters
    n_g = sum(x.numel() for x in model.parameters()
              if x.requires_grad)  # number gradients
    if verbose:
        print(f"{'layer':>5} {'name':>40} {'gradient':>9} {'parameters':>12} {'shape':>20} {'mu':>10} {'sigma':>10}")
        for i, (name, p) in enumerate(model.named_parameters()):
            name = name.replace('module_list.', '')
            print('%5g %40s %9s %12g %20s %10.3g %10.3g' %
                  (i, name, p.requires_grad, p.numel(), list(p.shape), p.mean(), p.std()))

    try:  # FLOPs
        p = next(model.parameters())
        stride = max(int(model.stride.max()), 32) if hasattr(
            model, 'stride') else 32  # max stride
        # input image in BCHW format
        im = torch.empty((1, p.shape[1], stride, stride), device=p.device)
        flops = thop.profile(deepcopy(model), inputs=(im, ), verbose=False)[
            0] / 1E9 * 2  # stride GFLOPs
        imgsz = imgsz if isinstance(imgsz, list) else [
            imgsz, imgsz]  # expand if int/float
        # 640x640 GFLOPs
        # fs = f', {flops * imgsz[0] / stride * imgsz[1] / stride:.1f} GFLOPs'
    except Exception:
        # fs = ''
        pass

    name = Path(model.yaml_file).stem.replace(
        'yolov5', 'YOLOv5') if hasattr(model, 'yaml_file') else 'Model'
    LOGGER.info(
        f'{name} summary: {len(list(model.modules()))} layers, {n_p} parameters, {n_g} gradients{fs}')
    # """


def scale_img(img, ratio=1.0, same_shape=False, gs=32):  # img(16,3,256,416)
    # Scales img(bs,3,y,x) by ratio constrained to gs-multiple
    if ratio == 1.0:
        return img
    h, w = img.shape[2:]
    s = (int(h * ratio), int(w * ratio))  # new size
    img = F.interpolate(img, size=s, mode='bilinear',
                        align_corners=False)  # resize
    if not same_shape:  # pad/crop img
        h, w = (math.ceil(x * ratio / gs) * gs for x in (h, w))
    # value = imagenet mean
    return F.pad(img, [0, w - s[1], 0, h - s[0]], value=0.447)

"""
def copy_attr(a, b, include=(), exclude=()):
    print("aaa")
    # Copy attributes from b to a, options to only include [...] and to exclude [...]
    for k, v in b.__dict__.items():
        if (len(include) and k not in include) or k.startswith('_') or k in exclude:
            continue
        else:
            setattr(a, k, v)
"""
