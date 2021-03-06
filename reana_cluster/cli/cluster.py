# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# REANA is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# REANA; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization or
# submit itself to any jurisdiction.
"""REANA cluster administration (init, restart, etc.) commands."""


import errno
import logging
import os

import click
import yaml

from ..config import (generated_cluster_conf_default_path,
                      reana_env_exportable_info_components)


@click.command(help='Bring REANA cluster down, i.e. delete all '
                    'deployed components.')
@click.option(
    '--remove-persistent-storage',
    is_flag=True,
    help='NOT IMPLEMENTED.\n'
         'If set, also persistent storage inside the cluster is deleted.')
@click.pass_context
def down(ctx, remove_persistent_storage):
    """Bring REANA cluster down, i.e. deletes all deployed components."""
    try:
        ctx.obj.backend.down()
    except Exception as e:
        logging.debug(str(e))


@click.command(help='Fetch information (e.g. URLs) about a REANA component '
                    'deployed in REANA cluster.')
@click.argument('component')
@click.option(
    '--namespace',
    default='default',
    help='Namespace of the component which URL should be resolved.')
@click.pass_context
def get(ctx, component, namespace):
    """Fetch URL for a REANA component running in REANA cluster."""
    try:
        component_info = ctx.obj.backend.get_component(component, namespace)

        for key, value in component_info.items():
            click.echo('{}: {}'.format(key, value))

    except Exception as e:
        logging.debug(str(e))


@click.command(help='Display the commands to set up the environment for the '
                    'REANA client.')
@click.option(
    '--namespace',
    default='default',
    help='Namespace of the components which configuration should be produced.')
@click.pass_context
def env(ctx, namespace):
    """Produce shell exportable list of REANA components' urls."""
    try:
        export_lines = []
        component_export_line = 'export {env_variable_name}={component_url}'
        for component in reana_env_exportable_info_components:
            component_info = ctx.obj.backend.get_component(
                component, namespace)
            export_lines.append(component_export_line.format(
                env_variable_name='{0}_URL'.format(
                    component.upper().replace('-', '_')),
                component_url='{schema}://{ip}:{port}'.format(
                    schema='http',
                    ip=component_info['external_ip_s'][0],
                    port=component_info['ports'][0]),
            ))
        click.echo('\n'.join(export_lines))
    except Exception as e:
        logging.debug(str(e))


@click.command(help='NOT IMPLEMENTED.\n'
                    'Restart components running in REANA cluster.')
@click.option(
    '--remove-persistent-storage',
    is_flag=True,
    help='NOT IMPLEMENTED.\n'
         'If set, also persistent storage inside the cluster is deleted.')
@click.pass_context
def restart(ctx, remove_persistent_storage):
    """Restart all components running in REANA cluster."""
    try:
        ctx.obj.backend.restart()
    except Exception as e:
        logging.debug(str(e))


@click.command(help="Initialize REANA cluster, i.e. deploy all REANA "
                    "components to cluster type (e.g. 'kubernetes') "
                    "defined in REANA cluster specifications file")
@click.option(
    '--skip-initialization', is_flag=True,
    help='If set, configuration files for selected cluster type are '
         'generated, but cluster is not initialized.')
@click.option(
    '-o',
    '--output',
    type=click.Path(exists=False, resolve_path=False),
    help='Path where generated cluster configuration files should be saved.'
         'If no value is given no files are outputted.')
@click.pass_context
def init(ctx, skip_initialization, output):
    """Initialize REANA cluster."""
    try:
        backend = ctx.obj.backend

        if not skip_initialization:
            logging.info('Connecting to {cluster} at {url}'
                         .format(cluster=backend.cluster_type,
                                 url=backend.cluster_url))
            backend.init()

        if output:
            path = click.format_filename(output)
            logging.info('Writing deployable REANA cluster configuration '
                         'to {0}'.format(path))

            for manifest in backend.cluster_conf:

                folder = os.path.join(path, manifest['kind'].lower() + 's')
                filename = manifest['metadata']['name'] + '-manifest.yaml'
                filepath = os.path.join(folder, filename)

                # Create folders if they don't exist
                # Based on: https://stackoverflow.com/a/12517490
                if not os.path.exists(os.path.dirname(filepath)):
                    try:
                        os.makedirs(os.path.dirname(filepath))
                    except OSError as exc:  # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise

                with click.open_file(filepath, mode='w+') as output_file:
                    yaml.dump(manifest, output_file, default_flow_style=False)

        click.echo("Init complete")

    except Exception as e:
        logging.exception(str(e))


@click.group(chain=True,
             invoke_without_command=True,
             help='Verify that configuration of REANA cluster and '
                  'components deployed there are set up according to '
                  'REANA cluster specifications file.')
@click.pass_context
def verify(ctx):
    """Verify configuration of running cluster and deployed components."""
    try:
        # If user didn't supply any sub-commands execute complete verification
        if ctx.invoked_subcommand is None:
            cli_verify_backend(ctx)
            cli_verify_components(ctx)

    except Exception as e:
        logging.debug(str(e))


@click.command('backend',
               help='Only verify that configuration of REANA cluster matches '
                    'to what is specified in REANA cluster specifications '
                    'file.')
@click.pass_context
def cli_verify_backend(ctx):
    """Verify configuration of running cluster backend."""
    logging.debug(ctx.obj.backend.cluster_spec)
    backend_compatibility = ctx.obj.backend.verify_backend()
    click.echo('Kubernetes Server {0} ... {1}.'
               .format(backend_compatibility['current_version'],
                       'OK' if backend_compatibility['is_compatible']
                       else 'ERROR'))


@click.command('components',
               help='Only verify that configuration of REANA components '
                    'deployed to REANA cluster matches to what is specified '
                    'in REANA cluster specifications file.')
@click.pass_context
def cli_verify_components(ctx):
    """Verify configuration of components deployed in a running cluster."""
    logging.debug(ctx.obj.backend.cluster_spec)
    matching_components = ctx.obj.backend.verify_components()
    for component_name in matching_components:
        click.echo('reana-{0} ... {1}.'
                   .format(component_name,
                           'OK' if matching_components[component_name]
                           else 'ERROR'))


verify.add_command(cli_verify_backend)
verify.add_command(cli_verify_components)
