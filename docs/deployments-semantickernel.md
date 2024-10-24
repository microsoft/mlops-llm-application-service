# Deployment options for Semantic Kernel

This document covers the various options for deploying Semantic Kernel

## Deploy using Logic Apps with Semantic Kernel as a plugin

* Import the [Logic App as a plugin into Semantic Kernel](https://devblogs.microsoft.com/semantic-kernel/connect-logic-apps-1400-connectors-to-semantic-kernel/#use-logic-apps-with-semantic-kernel-as-a-plugin) using the OpenAPI import method. Integrating Logic Apps as a plugin into Semantic Kernel enhances its functionality by providing access to over 1000 connectors. This integration allows for seamless connections with cloud services, on-premises systems, and hybrid environments. By using these plugins, customers can automate complex workflows, trigger actions, and interact with multiple systems. They can also effortlessly integrate their applications with diverse external systems, enabling them to leverage advanced features without the need for extensive custom development, thus saving time and resources. Since Logic Apps is built on `Function runtime` as well, you should be able to follow most of what in the above post to hookup Function app to SK.
* When you [create your plugin](https://techcommunity.microsoft.com/t5/azure-integration-services-blog/integrate-logic-app-workflows-as-plugins-with-semantic-kernel/ba-p/4210854), you'll want to provide custom HTTP client that can handle authentication for your Logic App. This will allow you to use the plugin in your AI agents without needing to worry about the authentication. It uses interactive auth to acquire a token and authenticate the user for the Logic App.


## Deploy as a containerized app in Serverless Container Service (Azure Container Apps)

* Deploy Semantic Kernel service as a container image and automatic scaling based on HTTP traffic(manged via AKS under the hood)
* Also, integrates with KEDA for event driven scaling, Dapr for building microservices.

![Deploy in a container app](./images/sk-deploy-containerApps.png?raw=true)

## Deploy as a containerized app in Azure Kubernetes service(AKS)

* Deploying a Semantic Kernel application on Azure Kubernetes Service(AKS) allows you to leverage the scalability, flexibility and robustness of kubernetes while integrating advanced AI capabilities into your applications. 

![Deploy in AKS](./images/sk-deploy-aks.png?raw=true)


  