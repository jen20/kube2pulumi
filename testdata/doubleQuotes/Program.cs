using System.Collections.Generic;
using Pulumi;
using Kubernetes = Pulumi.Kubernetes;

return await Deployment.RunAsync(() => 
{
    var argocd_serverDeployment = new Kubernetes.Apps.V1.Deployment("argocd_serverDeployment", new()
    {
        ApiVersion = "apps/v1",
        Kind = "Deployment",
        Metadata = new Kubernetes.Types.Inputs.Meta.V1.ObjectMetaArgs
        {
            Labels = 
            {
                { "app.kubernetes.io/component", "server" },
                { "app.kubernetes.io/instance", "argocd" },
                { "app.kubernetes.io/managed-by", "pulumi" },
                { "app.kubernetes.io/name", "argocd-server" },
                { "app.kubernetes.io/part-of", "argocd" },
                { "app.kubernetes.io/version", "v1.6.1" },
                { "helm.sh/chart", "argo-cd-2.5.4" },
            },
            Name = "argocd-server",
        },
        Spec = new Kubernetes.Types.Inputs.Apps.V1.DeploymentSpecArgs
        {
            Template = new Kubernetes.Types.Inputs.Core.V1.PodTemplateSpecArgs
            {
                Spec = new Kubernetes.Types.Inputs.Core.V1.PodSpecArgs
                {
                    Containers = new[]
                    {
                        new Kubernetes.Types.Inputs.Core.V1.ContainerArgs
                        {
                            ReadinessProbe = new Kubernetes.Types.Inputs.Core.V1.ProbeArgs
                            {
                                HttpGet = new Kubernetes.Types.Inputs.Core.V1.HTTPGetActionArgs
                                {
                                    Port = 8080,
                                },
                            },
                        },
                    },
                },
            },
        },
    });

});

