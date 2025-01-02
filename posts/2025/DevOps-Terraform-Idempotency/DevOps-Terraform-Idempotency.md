---
title: Terraform - Mastering Idempotency Violations - Handling Resource Conflicts and Failures in Azure
published: false
description: DevOps - Terraform - Mastering Idempotency Violations by Handling Resource Conflicts and Failures in Azure
tags: 'terraform, azure, iac, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/DevOps-Terraform-Idempotency/assets/main-tf-error.png'
canonical_url: null
id: 2183449
series: Terraform ERRORS!
---

## Idempotency: The Backbone of Terraform

Welcome to a new Terraform blog post series, **[Terraform ERRORS!]()** In this series, we will explore common errors and issues that you may encounter when working with Terraform and how to resolve them.  

**Idempotency** is one of **Terraform's** most powerful features, ensuring that you can apply your **infrastructure code** multiple times and always get the same result. This consistency is essential for managing **Azure cloud resources** like **virtual machines**, **storage accounts**, **databases**, in addition **permissions and RBAC** and much more efficiently. But what happens when idempotency breaks or cannot be maintained due to various reasons outside of our control? How do we handle these violations and ensure that our infrastructure remains consistent and reliable and more robust to better handle these violations?  

In this series, we will focus mainly on **idempotency violations** and how to handle them when working with **Terraform** and **Microsoft Azure**. These errors are normally classed under `StatusCode=409` and can be difficult to troubleshoot and resolve as they do not show up in the **Terraform plan**, but will fail during the **Terraform apply**.  

Let's dive in!

---

## Common Idempotency Violations using Terraform

When **idempotency breaks**, it can lead to issues such as **Duplicate Key/Entry Error**, **Resource Conflict Errors**, or **Already Exists Errors**. Understanding what idempotency means in **practical scenarios** and knowing how to resolve these failures is crucial for maintaining **reliable Infrastructure as Code**. The main problem with certain idempotency violations is that the terraform plan will not show any errors, but the apply will fail.

Let's look at a common example of a **idempotency violation** when working with **Terraform** and **Microsoft Azure** and see how to best handle it.  

### Role Assignment (RBAC) Already Exists

**Scenario:** You try to create an RBAC/IAM permission in Azure, but it already exists (perhaps it was created outside of Terraform or during a previous run).

**Example:**

```hcl
# Create a Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

# Write a resource creation of a user assigned managed identity
resource "azurerm_user_assigned_identity" "uai" {
  name                = "${var.resource_group_name}-uai"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

# Create a role assignment (twice to cause the violation)
resource "azurerm_role_assignment" "rbac" {
  count                = 2
  principal_id         = azurerm_user_assigned_identity.uai.principal_id
  role_definition_name = "Contributor"
  scope                = azurerm_resource_group.rg.id
}
 ```

In the above example we simulate the violation by creating two role assignments with the `same principal_id`, `role_definition_name` and `scope` using `count=2`. As you can see the plan will not show any errors, but the apply will fail.  

**Terraform Plan:**

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/DevOps-Terraform-Idempotency/assets/plan1.png)  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/DevOps-Terraform-Idempotency/assets/plan2.png)

**Error Message:**

  ```bash
╷
│ Error: authorization.RoleAssignmentsClient#Create: Failure responding to request: StatusCode=409 -- Original Error: autorest/azure: Service returned an error. Status=409 Code="RoleAssignmentExists" Message="The role assignment already exists."
│ 
│   with azurerm_role_assignment.rbac[0],
│   on foundation_resources.tf line 22, in resource "azurerm_role_assignment" "rbac":
│   22: resource "azurerm_role_assignment" "rbac" {
│ 
╵
  ```

As you can see the error message, it is clear that the role assignment already exists!

```bash
Status=409 Code="RoleAssignmentExists" Message="The role assignment already exists.
```

**Cause:** In a real world scenarios, this violation can happen when the role assignment was created outside of Terraform, for example by an **Operations** or **security** team, or by **Azure Policy** to enforce certain security or operational conditions, or perhaps the permission was set as part of a previous different Terraform configuration with a separate state file. So when our current Terraform configuration tries to create the role assignment again, it fails as the permission already exists.  

---

### **Solution 1:** Add Conditions using a `variable` flag/switch

This is not the best method in my personal opinion, but in the following solution we can create a condition to control the `azurerm_role_assignment` resource to create the role assignment only if the variable `create_role_assignment` is set to `true`. This way we can avoid the violation by creating the role assignment only when needed.  

```hcl
variable "create_role_assignment" {
  description = "Flag to create the role assignment"
  type        = bool
  default     = false
}

resource "azurerm_role_assignment" "rbac" {
  count                = var.create_role_assignment ? 1 : 0
  principal_id         = azurerm_user_assigned_identity.uai.principal_id
  role_definition_name = "Contributor"
  scope                = azurerm_resource_group.rg.id
}
```

This method is useful when you want to create the role assignment conditionally but is somewhat limited as it will not work if you have multiple user assigned identities or have multiple role definitions.

---

## **Solution 2:** Use `null_resource` with a `local-exec` provisioner using `az` CLI to create the role assignment

Another way to handle the violation is by using a `null_resource` with a `local-exec` provisioner to create role assignments. This way we can avoid the violation by creating the role assignment using `az` CLI only when needed. This method is useful when you want to create the role assignment conditionally and is more flexible as it can be used with multiple user assigned identities or multiple role definitions as using `az`.

```hcl
# Create a null resource with a local-exec provisioner to create the role assignment for 'contributor' and 'reader' from a var.permissions list
# Using classic 'az' login to authenticate and create the role assignment
resource "null_resource" "rbac" {
  for_each = toset(["Contributor", "Reader"])
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = <<EOT
      az login --service-principal --username $ARM_CLIENT_ID --password $ARM_CLIENT_SECRET --tenant $ARM_TENANT_ID --output none
      az account set --subscription $ARM_SUBSCRIPTION_ID --output none
      az role assignment create --assignee ${azurerm_user_assigned_identity.uai.principal_id} --role ${each.key} --scope ${azurerm_resource_group.rg.id}
    EOT
  }
}
```

In the above example we use a `null_resource` with a `local-exec` provisioner to create the role assignment. Since we know that th contributor role already exists which causes the violation, we can skip it and only create the reader role assignment. This way we can avoid the violation by creating the role assignment only when needed. The only downside to this method is that it uses the `az` CLI to create the role assignment which may not be available in all environments or may require additional setup on the build agent.  

The other downside is that the `null_resource` does not have a state file, so it will not be managed by Terraform and will not be shown in the plan or apply. This means that if the role assignment is deleted outside of Terraform, Terraform will not know about it and will not recreate it. This can be a problem if you want to keep your infrastructure in sync with your code and want to avoid manual changes to the infrastructure.  

**IMPORTANT!:** When using `az` CLI like this you need to be aware that you will need a way for your agent to also authenticate to Azure and have the necessary permissions to create the role assignment. This can be done by setting the environment variables `ARM_CLIENT_ID`, `ARM_CLIENT_SECRET`, `ARM_TENANT_ID` and `ARM_SUBSCRIPTION_ID` on the build agent to use a service principal with the necessary permissions. As you can see from the command above, we are using a service principal to authenticate to Azure and create the role assignment.  

```azurecli
az login --service-principal --username $ARM_CLIENT_ID --password $ARM_CLIENT_SECRET --tenant $ARM_TENANT_ID --output none
az account set --subscription $ARM_SUBSCRIPTION_ID --output none
az role assignment create --assignee ${azurerm_user_assigned_identity.uai.principal_id} --role ${each.key} --scope ${azurerm_resource_group.rg.id}
```

If you are using GitHub Actions, you can set these environment variables in the GitHub Secrets and use them in your workflow.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/DevOps-Terraform-Idempotency/assets/github-secrets.png)

Federated tokens via OIDC or other methods can also be used to authenticate to Azure and create the role assignment using the `az` CLI in the `local-exec` provisioner. For more details on how to authenticate to Azure using the `az` CLI, see **[Authenticate Azure CLI](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli/?wt.mc_id=DT-MVP-5004771)**

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/DevOps-Terraform-Idempotency/assets/azure-login.png)

## solution 3: Use `terraform_data` instead of `null_resource` to create the role assignment

## solution 4: Use a `local-exec` provisioner to create the role assignment for Special Cases

Provisioners are useful in rare cases when you need to run a script or external command during Terraform's execution. However, they should generally be a last resort because they break Terraform's declarative model and can lead to unpredictable behaviour.

Unlike `data` sources, provisioners do not integrate with Terraform's state or lifecycle management. Just like in the previous example, the `local-exec` provisioner is used to run the `az` CLI to create the role assignment. This way we can avoid the violation by creating the role assignment only when needed. However the main issues remain the same, if a provisioner fails or produces unexpected results, Terraform may not recover gracefully or recognise the issue during future runs. Data sources, on the other hand, allow Terraform to query existing infrastructure and make decisions based on the current state, ensuring better consistency and reliability.

```hcl
#Create a role assignment with a local-exec provisioner to create the role assignment
resource "azurerm_role_assignment" "rbac" {
  for_each = toset(["Contributor", "Reader"])
  role_definition_name = each.value
  scope = azurerm_resource_group.rg.id
  principal_id = azurerm_user_assigned_identity.uai.principal_id

  provisioner "local-exec" {
    command = <<EOT
      if ! az role assignment list --scope ${azurerm_resource_group.rg.id} --assignee ${azurerm_user_assigned_identity.uai.principal_id} --role ${each.value} --query [].roleDefinitionName -o tsv; then
        echo "Role assignment does not exist. Proceeding with creation."
        exit 0
      else
        echo "Role assignment already exists. Skipping creation."
        exit 1
      fi
    EOT
    interpreter = ["bash", "-c"]
  }

  lifecycle {
    ignore_changes = [provisioner]
  }
}
```

In the above example we use a `local-exec` provisioner to run the `az` CLI to check if the role assignment we want to add already exists. Based on our earlier violation we know that `Contributor` already exists, (perhaps it was created outside of Terraform by an **Operations** or **Security** team, or during a previous run of another module perhaps with its own state file separate to this run), so we would want to skip the roles that exist and only create the ones we do not have yet e.g. `Reader` with the `local-exec` provisioner. This way we can avoid the violation by creating the role assignment after checking and only when needed. 

---

## Best Practices to Avoid Problems with Idempotency

1. **Import Existing Resources:** Add unmanaged resources to Terraform's state before applying changes. but in some cases, this may not be possible or practical due to the complexity of the resource or the number of resources or teams involved in managing them when it comes to permissions and RBAC. So if the permissions and RBAC are managed by different teams or are created outside of Terraform, it may be better to use the `data` resource method to check and create the role assignments conditionally.
2. **Use Data Sources:** Query existing resources to make decisions in your code.
3. **Add Conditions:** based on the data source results to create resources conditionally.
4. **Ignore Unimportant Changes:** Use lifecycle rules to avoid unnecessary updates and changes.
5. **Limit Provisioners:** Only use provisioners for tasks Terraform can't handle natively or for last resort special cases.
6. **Plan Before Apply:** Always run `terraform plan` before applying your configuration. This step helps you preview the changes Terraform will make, ensuring they align with your expectations. For beginners, planning is especially critical as it can catch common issues like misconfigurations or unintended resource changes before they happen. It's a simple but powerful way to avoid surprises and maintain control over your infrastructure. Always run `terraform plan` to preview changes and catch potential issues early. But remember that the plan will not show any errors for the violation, so you will need to check the apply output for the error message in these cases.
7. **Sync with Cloud State:** Use `terraform refresh` to update Terraform’s state before applying changes.

---

## Conclusion

Idempotency makes **Terraform** a reliable tool for managing cloud infrastructure. By understanding common problems and using the strategies in this blog, you can avoid errors and keep your infrastructure predictable. Whether you're working on Azure RBAC or other setups, these tips will help you write better Terraform configurations. With careful planning and good practices, you can ensure that Terraform runs smoothly and efficiently every time.

**Have you faced idempotency problems in Terraform? Share your solutions in the comments!**

If you enjoyed this post and want to learn more about **Terraform** and **Azure**, check out my other Terraform Series **[Terraform Pro Tips](https://dev.to/pwd9000/series/16567)**.

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X/Twitter](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
