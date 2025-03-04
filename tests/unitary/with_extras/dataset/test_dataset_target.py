#!/usr/bin/env python

# Copyright (c) 2023 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

import os
from typing import Tuple
import pandas as pd
import pytest
from ads.dataset.classification_dataset import BinaryClassificationDataset
from ads.dataset.dataset_with_target import ADSDatasetWithTarget
from ads.dataset.pipeline import TransformerPipeline
from ads.dataset.target import TargetVariable


class TestADSDatasetTarget:
    def test_initialize_dataset_target(self):
        employees = ADSDatasetWithTarget(
            df=pd.read_csv(self.get_data_path()),
            target="Attrition",
            name="test_dataset",
            description="test_description",
            storage_options={'config':{},'region':'us-ashburn-1'}
        )

        assert isinstance(employees, ADSDatasetWithTarget)
        assert employees.name == "test_dataset"
        assert employees.description == "test_description"
        self.assert_dataset(employees)

    def test_dataset_target_from_dataframe(self):
        employees = ADSDatasetWithTarget.from_dataframe(
            df=pd.read_csv(self.get_data_path()),
            target="Attrition",
            storage_options={'config':{},'region':'us-ashburn-1'}
        ).set_positive_class('Yes')

        assert isinstance(employees, BinaryClassificationDataset)
        self.assert_dataset(employees)

    def test_accessor_with_target(self):
        df=pd.read_csv(self.get_data_path())
        employees = df.ads.dataset_with_target(
            target="Attrition"
        )

        assert isinstance(employees, BinaryClassificationDataset)
        self.assert_dataset(employees)

    def test_accessor_with_target_error(self):
        df=pd.read_csv(self.get_data_path())
        wrong_column = "wrong_column"
        with pytest.raises(
            ValueError, match=f"{wrong_column} column doesn't exist in data frame. Specify a valid one instead."
        ):
            employees = df.ads.dataset_with_target(
                target=wrong_column
            )

    def assert_dataset(self, dataset):
        assert isinstance(dataset.df, pd.DataFrame)
        assert isinstance(dataset.shape, Tuple)
        assert isinstance(dataset.target, TargetVariable)
        assert dataset.target.type["type"] == "categorical"
        assert "type_discovery" in dataset.init_kwargs
        assert isinstance(dataset.transformer_pipeline, TransformerPipeline)

    def get_data_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "data", "orcl_attrition.csv")
