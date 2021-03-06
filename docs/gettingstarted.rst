.. _gettingstarted:

Getting started
===============

This tutorial explains how to quick-start with REANA-Cluster.

Deploy REANA cluster locally
----------------------------

Are you looking at installing and deploying REANA cluster locally on your laptop?

1. Install `kubectl <https://kubernetes.io/docs/tasks/tools/install-kubectl/>`_
   and `minikube <https://kubernetes.io/docs/tasks/tools/install-minikube/>`_.

2. Start Minikube virtual machine:

.. code-block:: console

   $ minikube start --kubernetes-version="v1.6.4"

3. Install REANA-Cluster sources. You probably want to use a virtual environment:

.. code-block:: console

   $ mkvirtualenv reana-cluster
   $ pip install reana-cluster

4. Start REANA cluster instance on Minikube:

.. code-block:: console

   $ reana-cluster init

5. Check the status of deployed REANA cluster components:

.. code-block:: console

   $ reana-cluster verify components

6. Check whether all the pods are running:

.. code-block:: console

   $ kubectl get pods

7. Display the commands to set up the environment for the REANA client:

.. code-block:: console

   $ reana-cluster env
   export REANA_SERVER_URL=http://192.168.99.100:32732


The REANA cluster is now ready to serve users. Please see the `reana-client
<https://reana-client.readthedocs.io/>`_ documentation on how to run reusable
analysis examples on our locally-deployed cluster.

Note that after you finish testing REANA, you can delete the locally-deployed
cluster and the Minikube virtual machine as follows:

.. code-block:: console

  $ reana-cluster down
  $ minikube stop

Next steps
----------

For more information, please see:

- Looking for a more comprehensive user manual? See :ref:`userguide`
- Looking for tips how to develop REANA-Cluster component? See :ref:`developerguide`
- Looking for command-line API reference? See :ref:`cliapi`
