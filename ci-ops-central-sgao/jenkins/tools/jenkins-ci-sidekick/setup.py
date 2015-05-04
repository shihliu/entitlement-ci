from setuptools import setup, find_packages

setup(
    name="jenkins-ci-sidekick",
    version="0.0.2",
    author="jflynn",
    author_email="jflynn@redhat.com",
    description="Manage CI Jenkins plugin with YAML.",
    keywords="jenkins, plugin",
    packages=find_packages(),
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],
    entry_points={
        'jenkins_jobs.triggers': [
            'ci-trigger=jenkins_ci_sidekick.modules.triggers:ci_trigger'
        ],
        'jenkins_jobs.publishers': [
            'ci-publisher=jenkins_ci_sidekick.modules.publishers:ci_publisher'
        ],
    }

)
