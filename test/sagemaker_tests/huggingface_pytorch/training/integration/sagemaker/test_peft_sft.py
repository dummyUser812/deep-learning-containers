# Copyright 2018-2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from __future__ import absolute_import

import pytest
import sagemaker
from sagemaker.huggingface import HuggingFace

from ..... import invoke_sm_helper_function
from ...integration import DEFAULT_TIMEOUT, peft_sft_script
from ...integration.sagemaker.timeout import timeout


@pytest.mark.processor("gpu")
@pytest.mark.model("hf-peft-trl")
@pytest.mark.gpu_test
@pytest.mark.skip_py2_containers
@pytest.mark.team("sagemaker-1p-algorithms")
def test_diffusers(ecr_image, sagemaker_regions, py_version, instance_type):
    invoke_sm_helper_function(
        ecr_image, sagemaker_regions, _test_diffusers_model, py_version, instance_type, 1
    )


def _test_diffusers_model(
    ecr_image,
    sagemaker_session,
    py_version,
    instance_type,
    instance_count,
):
    # hyperparameters, which are passed into the training job
    hyperparameters = {
        "model_id": "trl-internal-testing/dummy-GPT2-correct-vocab",
        "output_dir": "/opt/ml/model",
        "train_batch_size": 2,
        "max_steps": 4,
        "eval_steps": 2,
        "save_steps": 2,
        "rank": 16,
        "lora_alpha": 32,
        "lora_dropout": 0.05,
    }

    with timeout(minutes=DEFAULT_TIMEOUT):
        estimator = HuggingFace(
            entry_point=peft_sft_script,
            role="SageMakerRole",
            image_uri=ecr_image,
            instance_count=instance_count,
            instance_type=instance_type,
            sagemaker_session=sagemaker_session,
            py_version=py_version,
            hyperparameters=hyperparameters,
        )
        estimator.fit(job_name=sagemaker.utils.unique_name_from_base("test-hf-peft-trl"))
