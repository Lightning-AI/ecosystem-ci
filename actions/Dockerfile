# Copyright The PyTorch Lightning team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ARG PYTORCH_VERSION=1.8.1
ARG CUDA_VERSION=11.1

# https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes
#FROM nvcr.io/nvidia/pytorch:${PYTORCH_VERSION}-py3
FROM pytorch/pytorch:${PYTORCH_VERSION}-cuda${CUDA_VERSION}-cudnn8-runtime

LABEL maintainer="Lightning-AI <https://github.com/Lightning-AI>"

RUN apt-get update -qq --fix-missing  && \
    apt-get install -y --no-install-recommends \
        sudo \
        build-essential \
        pkg-config \
        cmake \
        git \
        wget \
        curl \
        unzip \
        ca-certificates \
        software-properties-common \
        tree \
    && \

# Cleaning
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /root/.cache
