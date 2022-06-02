#!/usr/bin/env python
# -*- coding: utf-8; -*-

# Copyright (c) 2022 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

from logging import getLogger
from collections import namedtuple
import fsspec
import yaml
import importlib
from ads.opctl.config.yaml_parsers import YamlSpecParser

logger = getLogger("ads.yaml")


class DistributedSpecParser(YamlSpecParser):
    def __init__(self, distributed):
        # TODO: validate yamlInput
        self.distributed = distributed

    def parse(self):
        ClusterInfo = namedtuple(
            "ClusterInfo", field_names=["infrastructure", "cluster", "runtime"]
        )
        self.distributed_spec = self.distributed["spec"]
        infrastructure = self.distributed_spec["infrastructure"]
        cluster_def = self.distributed_spec["cluster"]
        cluster = self.parse_cluster(cluster_def)
        runtime = self.parse_runtime(self.distributed_spec.get("runtime"))
        return ClusterInfo(
            infrastructure=infrastructure, cluster=cluster, runtime=runtime
        )

    def parse_cluster(self, cluster_def):
        Cluster = namedtuple(
            "Cluster",
            field_names=[
                "name",
                "type",
                "image",
                "work_dir",
                "config",
                "main",
                "worker",
                "ephemeral",
            ],
        )
        cluster_spec = cluster_def["spec"]
        name = cluster_spec.get("name")
        cluster_type = cluster_def.get("kind")
        image = cluster_spec.get("image")
        work_dir = cluster_spec.get("workDir")
        ephemeral = cluster_spec.get("ephemeral")
        cluster_default_config = cluster_spec.get("config")
        main = self.parse_main(cluster_spec.get("main"))
        worker = self.parse_worker(cluster_spec.get("worker"))
        translated_config = self.translate_config(cluster_default_config)
        logger.debug(
            f"Cluster: [name: {name}, type: {cluster_type}, image: {image}, work_dir: {work_dir}, config: {translated_config}, main: {main}, worker: {worker}]"
        )
        return Cluster(
            name=name,
            type=cluster_type,
            image=image,
            work_dir=work_dir,
            config=translated_config,
            main=main,
            worker=worker,
            ephemeral=ephemeral,
        )

    def parse_main(self, main):
        Main = namedtuple("Main", field_names=["name", "image", "replicas", "config"])
        main_spec = main
        name = main_spec.get("name")
        replicas = main_spec.get("replicas") or 1
        if replicas > 1:
            logger.warn(
                "`replicas` greater than 1 is currently not supported. This will be default to 1"
            )
        image = main_spec.get("image")
        config = main_spec.get("config")
        translated_config = self.translate_config(config)
        logger.debug(
            f"main: [name: {name}, image: {image}, replicas: {replicas}, config: {translated_config}]"
        )
        return Main(name=name, image=image, replicas=replicas, config=translated_config)

    def parse_worker(self, worker):
        Worker = namedtuple(
            "Worker", field_names=["name", "image", "replicas", "config"]
        )
        worker_spec = worker
        name = worker_spec.get("name")
        replicas = worker_spec.get("replicas") or 1
        image = worker_spec.get("image")
        config = worker_spec.get("config")
        translated_config = self.translate_config(config)
        logger.debug(
            f"Worker: [name: {name}, image: {image}, replicas: {replicas}, config: {translated_config}]"
        )
        return Worker(
            name=name, image=image, replicas=replicas, config=translated_config
        )

    def parse_runtime(self, runtime):
        PythonRuntime = namedtuple(
            "PythonRuntime", field_names=["entry_point", "args", "kwargs", "envVars"]
        )
        python_spec = runtime["spec"]
        envVars = {}
        if python_spec.get("env"):
            envVars = {k["name"]: k["value"] for k in python_spec.get("env")}
        return PythonRuntime(
            entry_point=python_spec.get("entryPoint"),
            args=python_spec.get("args"),
            kwargs=python_spec.get("kwargs"),
            envVars=envVars,
        )
