import pulumi
import pulumi_kubernetes as kubernetes

default_cilium_daemon_set = kubernetes.apps.v1.DaemonSet("defaultCiliumDaemonSet",
    api_version="apps/v1",
    kind="DaemonSet",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="cilium",
        namespace="default",
        labels={
            "k8s-app": "cilium",
            "app.kubernetes.io/part-of": "cilium",
            "app.kubernetes.io/name": "cilium-agent",
        },
    ),
    spec=kubernetes.apps.v1.DaemonSetSpecArgs(
        selector=kubernetes.meta.v1.LabelSelectorArgs(
            match_labels={
                "k8s-app": "cilium",
            },
        ),
        update_strategy=kubernetes.apps.v1.DaemonSetUpdateStrategyArgs(
            rolling_update=kubernetes.apps.v1.RollingUpdateDaemonSetArgs(
                max_unavailable=2,
            ),
            type="RollingUpdate",
        ),
        template=kubernetes.core.v1.PodTemplateSpecArgs(
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                annotations={
                    "container.apparmor.security.beta.kubernetes.io/cilium-agent": "unconfined",
                    "container.apparmor.security.beta.kubernetes.io/clean-cilium-state": "unconfined",
                    "container.apparmor.security.beta.kubernetes.io/mount-cgroup": "unconfined",
                    "container.apparmor.security.beta.kubernetes.io/apply-sysctl-overwrites": "unconfined",
                },
                labels={
                    "k8s-app": "cilium",
                    "app.kubernetes.io/name": "cilium-agent",
                    "app.kubernetes.io/part-of": "cilium",
                },
            ),
            spec=kubernetes.core.v1.PodSpecArgs(
                containers=[kubernetes.core.v1.ContainerArgs(
                    name="cilium-agent",
                    image="quay.io/cilium/cilium:v1.14.2@sha256:6263f3a3d5d63b267b538298dbeb5ae87da3efacf09a2c620446c873ba807d35",
                    image_pull_policy="IfNotPresent",
                    command=["cilium-agent"],
                    args=["--config-dir=/tmp/cilium/config-map"],
                    startup_probe=kubernetes.core.v1.ProbeArgs(
                        http_get=kubernetes.core.v1.HTTPGetActionArgs(
                            host="127.0.0.1",
                            path="/healthz",
                            port=9879,
                            scheme="HTTP",
                            http_headers=[kubernetes.core.v1.HTTPHeaderArgs(
                                name="brief",
                                value="true",
                            )],
                        ),
                        failure_threshold=105,
                        period_seconds=2,
                        success_threshold=1,
                    ),
                    liveness_probe=kubernetes.core.v1.ProbeArgs(
                        http_get=kubernetes.core.v1.HTTPGetActionArgs(
                            host="127.0.0.1",
                            path="/healthz",
                            port=9879,
                            scheme="HTTP",
                            http_headers=[kubernetes.core.v1.HTTPHeaderArgs(
                                name="brief",
                                value="true",
                            )],
                        ),
                        period_seconds=30,
                        success_threshold=1,
                        failure_threshold=10,
                        timeout_seconds=5,
                    ),
                    readiness_probe=kubernetes.core.v1.ProbeArgs(
                        http_get=kubernetes.core.v1.HTTPGetActionArgs(
                            host="127.0.0.1",
                            path="/healthz",
                            port=9879,
                            scheme="HTTP",
                            http_headers=[kubernetes.core.v1.HTTPHeaderArgs(
                                name="brief",
                                value="true",
                            )],
                        ),
                        period_seconds=30,
                        success_threshold=1,
                        failure_threshold=3,
                        timeout_seconds=5,
                    ),
                    env=[
                        kubernetes.core.v1.EnvVarArgs(
                            name="K8S_NODE_NAME",
                            value_from=kubernetes.core.v1.EnvVarSourceArgs(
                                field_ref=kubernetes.core.v1.ObjectFieldSelectorArgs(
                                    api_version="v1",
                                    field_path="spec.nodeName",
                                ),
                            ),
                        ),
                        kubernetes.core.v1.EnvVarArgs(
                            name="CILIUM_K8S_NAMESPACE",
                            value_from=kubernetes.core.v1.EnvVarSourceArgs(
                                field_ref=kubernetes.core.v1.ObjectFieldSelectorArgs(
                                    api_version="v1",
                                    field_path="metadata.namespace",
                                ),
                            ),
                        ),
                        kubernetes.core.v1.EnvVarArgs(
                            name="CILIUM_CLUSTERMESH_CONFIG",
                            value="/var/lib/cilium/clustermesh/",
                        ),
                    ],
                    lifecycle=kubernetes.core.v1.LifecycleArgs(
                        pre_stop=kubernetes.core.v1.LifecycleHandlerArgs(
                            exec_=kubernetes.core.v1.ExecActionArgs(
                                command=["/cni-uninstall.sh"],
                            ),
                        ),
                    ),
                    security_context=kubernetes.core.v1.SecurityContextArgs(
                        se_linux_options=kubernetes.core.v1.SELinuxOptionsArgs(
                            level="s0",
                            type="spc_t",
                        ),
                        capabilities=kubernetes.core.v1.CapabilitiesArgs(
                            add=[
                                "CHOWN",
                                "KILL",
                                "NET_ADMIN",
                                "NET_RAW",
                                "IPC_LOCK",
                                "SYS_MODULE",
                                "SYS_ADMIN",
                                "SYS_RESOURCE",
                                "DAC_OVERRIDE",
                                "FOWNER",
                                "SETGID",
                                "SETUID",
                            ],
                            drop=["ALL"],
                        ),
                    ),
                    termination_message_policy="FallbackToLogsOnError",
                    volume_mounts=[
                        kubernetes.core.v1.VolumeMountArgs(
                            mount_path="/host/proc/sys/net",
                            name="host-proc-sys-net",
                        ),
                        kubernetes.core.v1.VolumeMountArgs(
                            mount_path="/host/proc/sys/kernel",
                            name="host-proc-sys-kernel",
                        ),
                        kubernetes.core.v1.VolumeMountArgs(
                            name="bpf-maps",
                            mount_path="/sys/fs/bpf",
                            mount_propagation="HostToContainer",
                        ),
                        kubernetes.core.v1.VolumeMountArgs(
                            name="cilium-run",
                            mount_path="/var/run/cilium",
                        ),
                        kubernetes.core.v1.VolumeMountArgs(
                            name="etc-cni-netd",
                            mount_path="/host/etc/cni/net.d",
                        ),
                        kubernetes.core.v1.VolumeMountArgs(
                            name="clustermesh-secrets",
                            mount_path="/var/lib/cilium/clustermesh",
                            read_only=True,
                        ),
                        kubernetes.core.v1.VolumeMountArgs(
                            name="lib-modules",
                            mount_path="/lib/modules",
                            read_only=True,
                        ),
                        kubernetes.core.v1.VolumeMountArgs(
                            name="xtables-lock",
                            mount_path="/run/xtables.lock",
                        ),
                        kubernetes.core.v1.VolumeMountArgs(
                            name="hubble-tls",
                            mount_path="/var/lib/cilium/tls/hubble",
                            read_only=True,
                        ),
                        kubernetes.core.v1.VolumeMountArgs(
                            name="tmp",
                            mount_path="/tmp",
                        ),
                    ],
                )],
                init_containers=[
                    kubernetes.core.v1.ContainerArgs(
                        name="config",
                        image="quay.io/cilium/cilium:v1.14.2@sha256:6263f3a3d5d63b267b538298dbeb5ae87da3efacf09a2c620446c873ba807d35",
                        image_pull_policy="IfNotPresent",
                        command=[
                            "cilium",
                            "build-config",
                        ],
                        env=[
                            kubernetes.core.v1.EnvVarArgs(
                                name="K8S_NODE_NAME",
                                value_from=kubernetes.core.v1.EnvVarSourceArgs(
                                    field_ref=kubernetes.core.v1.ObjectFieldSelectorArgs(
                                        api_version="v1",
                                        field_path="spec.nodeName",
                                    ),
                                ),
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="CILIUM_K8S_NAMESPACE",
                                value_from=kubernetes.core.v1.EnvVarSourceArgs(
                                    field_ref=kubernetes.core.v1.ObjectFieldSelectorArgs(
                                        api_version="v1",
                                        field_path="metadata.namespace",
                                    ),
                                ),
                            ),
                        ],
                        volume_mounts=[kubernetes.core.v1.VolumeMountArgs(
                            name="tmp",
                            mount_path="/tmp",
                        )],
                        termination_message_policy="FallbackToLogsOnError",
                    ),
                    kubernetes.core.v1.ContainerArgs(
                        name="mount-cgroup",
                        image="quay.io/cilium/cilium:v1.14.2@sha256:6263f3a3d5d63b267b538298dbeb5ae87da3efacf09a2c620446c873ba807d35",
                        image_pull_policy="IfNotPresent",
                        env=[
                            kubernetes.core.v1.EnvVarArgs(
                                name="CGROUP_ROOT",
                                value="/run/cilium/cgroupv2",
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="BIN_PATH",
                                value="/opt/cni/bin",
                            ),
                        ],
                        command=[
                            "sh",
                            "-ec",
                            """cp /usr/bin/cilium-mount /hostbin/cilium-mount;
              nsenter --cgroup=/hostproc/1/ns/cgroup --mount=/hostproc/1/ns/mnt "${BIN_PATH}/cilium-mount" $CGROUP_ROOT;
              rm /hostbin/cilium-mount
""",
                        ],
                        volume_mounts=[
                            kubernetes.core.v1.VolumeMountArgs(
                                name="hostproc",
                                mount_path="/hostproc",
                            ),
                            kubernetes.core.v1.VolumeMountArgs(
                                name="cni-path",
                                mount_path="/hostbin",
                            ),
                        ],
                        termination_message_policy="FallbackToLogsOnError",
                        security_context=kubernetes.core.v1.SecurityContextArgs(
                            se_linux_options=kubernetes.core.v1.SELinuxOptionsArgs(
                                level="s0",
                                type="spc_t",
                            ),
                            capabilities=kubernetes.core.v1.CapabilitiesArgs(
                                add=[
                                    "SYS_ADMIN",
                                    "SYS_CHROOT",
                                    "SYS_PTRACE",
                                ],
                                drop=["ALL"],
                            ),
                        ),
                    ),
                    kubernetes.core.v1.ContainerArgs(
                        name="apply-sysctl-overwrites",
                        image="quay.io/cilium/cilium:v1.14.2@sha256:6263f3a3d5d63b267b538298dbeb5ae87da3efacf09a2c620446c873ba807d35",
                        image_pull_policy="IfNotPresent",
                        env=[kubernetes.core.v1.EnvVarArgs(
                            name="BIN_PATH",
                            value="/opt/cni/bin",
                        )],
                        command=[
                            "sh",
                            "-ec",
                            """cp /usr/bin/cilium-sysctlfix /hostbin/cilium-sysctlfix;
              nsenter --mount=/hostproc/1/ns/mnt "${BIN_PATH}/cilium-sysctlfix";
              rm /hostbin/cilium-sysctlfix
""",
                        ],
                        volume_mounts=[
                            kubernetes.core.v1.VolumeMountArgs(
                                name="hostproc",
                                mount_path="/hostproc",
                            ),
                            kubernetes.core.v1.VolumeMountArgs(
                                name="cni-path",
                                mount_path="/hostbin",
                            ),
                        ],
                        termination_message_policy="FallbackToLogsOnError",
                        security_context=kubernetes.core.v1.SecurityContextArgs(
                            se_linux_options=kubernetes.core.v1.SELinuxOptionsArgs(
                                level="s0",
                                type="spc_t",
                            ),
                            capabilities=kubernetes.core.v1.CapabilitiesArgs(
                                add=[
                                    "SYS_ADMIN",
                                    "SYS_CHROOT",
                                    "SYS_PTRACE",
                                ],
                                drop=["ALL"],
                            ),
                        ),
                    ),
                    kubernetes.core.v1.ContainerArgs(
                        name="mount-bpf-fs",
                        image="quay.io/cilium/cilium:v1.14.2@sha256:6263f3a3d5d63b267b538298dbeb5ae87da3efacf09a2c620446c873ba807d35",
                        image_pull_policy="IfNotPresent",
                        args=["mount | grep \"/sys/fs/bpf type bpf\" || mount -t bpf bpf /sys/fs/bpf"],
                        command=[
                            "/bin/bash",
                            "-c",
                            "--",
                        ],
                        termination_message_policy="FallbackToLogsOnError",
                        security_context=kubernetes.core.v1.SecurityContextArgs(
                            privileged=True,
                        ),
                        volume_mounts=[kubernetes.core.v1.VolumeMountArgs(
                            name="bpf-maps",
                            mount_path="/sys/fs/bpf",
                            mount_propagation="Bidirectional",
                        )],
                    ),
                    kubernetes.core.v1.ContainerArgs(
                        name="clean-cilium-state",
                        image="quay.io/cilium/cilium:v1.14.2@sha256:6263f3a3d5d63b267b538298dbeb5ae87da3efacf09a2c620446c873ba807d35",
                        image_pull_policy="IfNotPresent",
                        command=["/init-container.sh"],
                        env=[
                            kubernetes.core.v1.EnvVarArgs(
                                name="CILIUM_ALL_STATE",
                                value_from=kubernetes.core.v1.EnvVarSourceArgs(
                                    config_map_key_ref=kubernetes.core.v1.ConfigMapKeySelectorArgs(
                                        name="cilium-config",
                                        key="clean-cilium-state",
                                        optional=True,
                                    ),
                                ),
                            ),
                            kubernetes.core.v1.EnvVarArgs(
                                name="CILIUM_BPF_STATE",
                                value_from=kubernetes.core.v1.EnvVarSourceArgs(
                                    config_map_key_ref=kubernetes.core.v1.ConfigMapKeySelectorArgs(
                                        name="cilium-config",
                                        key="clean-cilium-bpf-state",
                                        optional=True,
                                    ),
                                ),
                            ),
                        ],
                        termination_message_policy="FallbackToLogsOnError",
                        security_context=kubernetes.core.v1.SecurityContextArgs(
                            se_linux_options=kubernetes.core.v1.SELinuxOptionsArgs(
                                level="s0",
                                type="spc_t",
                            ),
                            capabilities=kubernetes.core.v1.CapabilitiesArgs(
                                add=[
                                    "NET_ADMIN",
                                    "SYS_MODULE",
                                    "SYS_ADMIN",
                                    "SYS_RESOURCE",
                                ],
                                drop=["ALL"],
                            ),
                        ),
                        volume_mounts=[
                            kubernetes.core.v1.VolumeMountArgs(
                                name="bpf-maps",
                                mount_path="/sys/fs/bpf",
                            ),
                            kubernetes.core.v1.VolumeMountArgs(
                                name="cilium-cgroup",
                                mount_path="/run/cilium/cgroupv2",
                                mount_propagation="HostToContainer",
                            ),
                            kubernetes.core.v1.VolumeMountArgs(
                                name="cilium-run",
                                mount_path="/var/run/cilium",
                            ),
                        ],
                        resources=kubernetes.core.v1.ResourceRequirementsArgs(
                            requests={
                                "cpu": "100m",
                                "memory": "100Mi",
                            },
                        ),
                    ),
                    kubernetes.core.v1.ContainerArgs(
                        name="install-cni-binaries",
                        image="quay.io/cilium/cilium:v1.14.2@sha256:6263f3a3d5d63b267b538298dbeb5ae87da3efacf09a2c620446c873ba807d35",
                        image_pull_policy="IfNotPresent",
                        command=["/install-plugin.sh"],
                        resources=kubernetes.core.v1.ResourceRequirementsArgs(
                            requests={
                                "cpu": "100m",
                                "memory": "10Mi",
                            },
                        ),
                        security_context=kubernetes.core.v1.SecurityContextArgs(
                            se_linux_options=kubernetes.core.v1.SELinuxOptionsArgs(
                                level="s0",
                                type="spc_t",
                            ),
                            capabilities=kubernetes.core.v1.CapabilitiesArgs(
                                drop=["ALL"],
                            ),
                        ),
                        termination_message_policy="FallbackToLogsOnError",
                        volume_mounts=[kubernetes.core.v1.VolumeMountArgs(
                            name="cni-path",
                            mount_path="/host/opt/cni/bin",
                        )],
                    ),
                ],
                restart_policy="Always",
                priority_class_name="system-node-critical",
                service_account="cilium",
                service_account_name="cilium",
                automount_service_account_token=True,
                termination_grace_period_seconds=1,
                host_network=True,
                affinity=kubernetes.core.v1.AffinityArgs(
                    pod_anti_affinity=kubernetes.core.v1.PodAntiAffinityArgs(
                        required_during_scheduling_ignored_during_execution=[kubernetes.core.v1.PodAffinityTermArgs(
                            label_selector=kubernetes.meta.v1.LabelSelectorArgs(
                                match_labels={
                                    "k8s-app": "cilium",
                                },
                            ),
                            topology_key="kubernetes.io/hostname",
                        )],
                    ),
                ),
                node_selector={
                    "kubernetes.io/os": "linux",
                },
                tolerations=[kubernetes.core.v1.TolerationArgs(
                    operator="Exists",
                )],
                volumes=[
                    kubernetes.core.v1.VolumeArgs(
                        name="tmp",
                        empty_dir=kubernetes.core.v1.EmptyDirVolumeSourceArgs(),
                    ),
                    kubernetes.core.v1.VolumeArgs(
                        name="cilium-run",
                        host_path=kubernetes.core.v1.HostPathVolumeSourceArgs(
                            path="/var/run/cilium",
                            type="DirectoryOrCreate",
                        ),
                    ),
                    kubernetes.core.v1.VolumeArgs(
                        name="bpf-maps",
                        host_path=kubernetes.core.v1.HostPathVolumeSourceArgs(
                            path="/sys/fs/bpf",
                            type="DirectoryOrCreate",
                        ),
                    ),
                    kubernetes.core.v1.VolumeArgs(
                        name="hostproc",
                        host_path=kubernetes.core.v1.HostPathVolumeSourceArgs(
                            path="/proc",
                            type="Directory",
                        ),
                    ),
                    kubernetes.core.v1.VolumeArgs(
                        name="cilium-cgroup",
                        host_path=kubernetes.core.v1.HostPathVolumeSourceArgs(
                            path="/run/cilium/cgroupv2",
                            type="DirectoryOrCreate",
                        ),
                    ),
                    kubernetes.core.v1.VolumeArgs(
                        name="cni-path",
                        host_path=kubernetes.core.v1.HostPathVolumeSourceArgs(
                            path="/opt/cni/bin",
                            type="DirectoryOrCreate",
                        ),
                    ),
                    kubernetes.core.v1.VolumeArgs(
                        name="etc-cni-netd",
                        host_path=kubernetes.core.v1.HostPathVolumeSourceArgs(
                            path="/etc/cni/net.d",
                            type="DirectoryOrCreate",
                        ),
                    ),
                    kubernetes.core.v1.VolumeArgs(
                        name="lib-modules",
                        host_path=kubernetes.core.v1.HostPathVolumeSourceArgs(
                            path="/lib/modules",
                        ),
                    ),
                    kubernetes.core.v1.VolumeArgs(
                        name="xtables-lock",
                        host_path=kubernetes.core.v1.HostPathVolumeSourceArgs(
                            path="/run/xtables.lock",
                            type="FileOrCreate",
                        ),
                    ),
                    kubernetes.core.v1.VolumeArgs(
                        name="clustermesh-secrets",
                        projected=kubernetes.core.v1.ProjectedVolumeSourceArgs(
                            default_mode=400,
                            sources=[
                                kubernetes.core.v1.VolumeProjectionArgs(
                                    secret=kubernetes.core.v1.SecretProjectionArgs(
                                        name="cilium-clustermesh",
                                        optional=True,
                                    ),
                                ),
                                kubernetes.core.v1.VolumeProjectionArgs(
                                    secret=kubernetes.core.v1.SecretProjectionArgs(
                                        name="clustermesh-apiserver-remote-cert",
                                        optional=True,
                                        items=[
                                            kubernetes.core.v1.KeyToPathArgs(
                                                key="tls.key",
                                                path="common-etcd-client.key",
                                            ),
                                            kubernetes.core.v1.KeyToPathArgs(
                                                key="tls.crt",
                                                path="common-etcd-client.crt",
                                            ),
                                            kubernetes.core.v1.KeyToPathArgs(
                                                key="ca.crt",
                                                path="common-etcd-client-ca.crt",
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    ),
                    kubernetes.core.v1.VolumeArgs(
                        name="host-proc-sys-net",
                        host_path=kubernetes.core.v1.HostPathVolumeSourceArgs(
                            path="/proc/sys/net",
                            type="Directory",
                        ),
                    ),
                    kubernetes.core.v1.VolumeArgs(
                        name="host-proc-sys-kernel",
                        host_path=kubernetes.core.v1.HostPathVolumeSourceArgs(
                            path="/proc/sys/kernel",
                            type="Directory",
                        ),
                    ),
                    kubernetes.core.v1.VolumeArgs(
                        name="hubble-tls",
                        projected=kubernetes.core.v1.ProjectedVolumeSourceArgs(
                            default_mode=400,
                            sources=[kubernetes.core.v1.VolumeProjectionArgs(
                                secret=kubernetes.core.v1.SecretProjectionArgs(
                                    name="hubble-server-certs",
                                    optional=True,
                                    items=[
                                        kubernetes.core.v1.KeyToPathArgs(
                                            key="tls.crt",
                                            path="server.crt",
                                        ),
                                        kubernetes.core.v1.KeyToPathArgs(
                                            key="tls.key",
                                            path="server.key",
                                        ),
                                        kubernetes.core.v1.KeyToPathArgs(
                                            key="ca.crt",
                                            path="client-ca.crt",
                                        ),
                                    ],
                                ),
                            )],
                        ),
                    ),
                ],
            ),
        ),
    ))
