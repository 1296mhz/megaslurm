from supermutes.dot import dotify

import sys
import unittest
import yaml


COMPILED_MANIFESTS_FILE = '/kubelint-compiled.yaml'
SKIP_LINT_ANNOTATION = 'lint.southbridge.io/skip'


def _skip_annotation(manifest):
    skip_annotations = manifest.metadata.get('annotations', {}).get(
            SKIP_LINT_ANNOTATION, ""
            ).split(', ')
    for skip_annotation in skip_annotations:
        if skip_annotation == sys._getframe(1).f_code.co_name.split(
                '_', 1
                )[1].replace('_', '-'):
            return True


class TestAll(unittest.TestCase):
    def setUp(self):
        self.all_manifests = []
        self.deployment_manifests = []
        self.ingress_manifests = []
        with open(COMPILED_MANIFESTS_FILE, 'r') as stream:
            for i in list(yaml.load_all(stream, Loader=yaml.FullLoader)):
                self.all_manifests.append(dotify(i))
        for manifest in self.all_manifests:
            if manifest.kind == "Deployment":
                self.deployment_manifests.append(manifest)
            elif manifest.kind == "Ingress":
                self.ingress_manifests.append(manifest)

    def test_labels(self):
        for manifest in self.all_manifests:
            with self.subTest(kind=manifest.kind, name=manifest.metadata.name):
                if not _skip_annotation(manifest):
                    try:
                        self.assertIn(
                            'app',
                            manifest.metadata.labels,
                            "{kind} {name} should contain app label, "
                            "to indicate which app is it".format(
                                kind=manifest.kind,
                                name=manifest.metadata.name
                                )
                            )
                        self.assertIn(
                            'component',
                            manifest.metadata.labels,
                            "{kind} {name} should contain component "
                            "label, to indicate which component is it".format(
                                kind=manifest.kind,
                                name=manifest.metadata.name
                                )
                            )
                        self.assertIn(
                            'release',
                            manifest.metadata.labels,
                            "{kind} {name} should contain release label, "
                            "to indicate which Helm release "
                            "this object belongs to".format(
                                kind=manifest.kind,
                                name=manifest.metadata.name
                                )
                            )
                    except KeyError:
                        self.fail(
                                '{kind} {name} does not contain labels'.format(
                                    kind=manifest.kind,
                                    name=manifest.metadata.name
                                    )
                                )
                else:
                    self.skipTest(
                            "{kind} {name} contains lint.southbridge.io/skip "
                            "annotation for this test".format(
                                kind=manifest.kind,
                                name=manifest.metadata.name
                            ))

    def test_not_latest_tag(self):
        for manifest in self.deployment_manifests:
            for container in manifest.spec.template.spec.containers:
                with self.subTest(
                        deployment=manifest.metadata.name,
                        container=container.name
                        ):
                    if not _skip_annotation(manifest):
                        self.assertNotEqual(
                                container.image.split(':')[-1],
                                'latest',
                                "Image tag of container {container} in "
                                "Deployment {name} should not "
                                "be 'latest'".format(
                                    container=container.name,
                                    name=manifest.metadata.name
                                    )
                                )
                    else:
                        self.skipTest(
                                "Deployment {name} contains "
                                "lint.southbridge.io/skip annotation "
                                "for this test".format(
                                    name=manifest.metadata.name
                                ))

    def test_minimum_replicas(self):
        for manifest in self.deployment_manifests:
            with self.subTest(manifest.metadata.name):
                if not _skip_annotation(manifest):
                    self.assertGreaterEqual(
                            manifest.spec.replicas,
                            2,
                            "Deployment {name} should have at least "
                            "two replicas".format(
                                name=manifest.metadata.name
                                )
                            )
                else:
                    self.skipTest(
                            "Deployment {name} contains "
                            "lint.southbridge.io/skip annotation "
                            "for this test".format(
                                name=manifest.metadata.name
                            ))

    def test_host(self):
        for manifest in self.ingress_manifests:
            for rule in manifest.spec.rules:
                with self.subTest(manifest.metadata.name):
                    if not _skip_annotation(manifest):
                        self.assertIn(
                                'host',
                                rule,
                                "Ingress {name} should contain host "
                                "field".format(name=manifest.metadata.name)
                                )
                    else:
                        self.skipTest(
                                "Ingress {name} contains "
                                "lint.southbridge.io/skip annotation "
                                "for this test".format(
                                    name=manifest.metadata.name
                                ))
