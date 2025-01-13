# Container app deployment

## Steps

Before running the CD for container app deployment of otel and financial analyst application, make sure the following are set as expected.

* Container App created in Azure portal with Ingress traffic allowing port 8080.
![Ingress config](./images/container_app_ingress_config.png)
* User Assigned Managed Identity created and is assigned to container app.
![User Assigned Managed Identity](./images/container_app_add_identity.png)
* Managed Identity(User Assigned) with respective RBAC roles are set for the sk_financial_analyst application.
![Managed identity Rbac Roles](./images/container_app_managed_identity_rbac.png)
* Application Insights resource created.
