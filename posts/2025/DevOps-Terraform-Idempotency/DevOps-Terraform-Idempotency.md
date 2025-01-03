---
title: Terraform - Mastering Idempotency Violations - Handling Resource Conflicts and Failures in Azure
published: true
description: DevOps - Terraform - Mastering Idempotency Violations by Handling Resource Conflicts and Failures in Azure
tags: 'terraform, azure, iac, azuredevops'
cover_image: 'https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/DevOps-Terraform-Idempotency/assets/main-tf-error.png'
canonical_url: null
id: 2183449
series: Terraform ERRORS!
---

## Idempotency: The Backbone of Terraform

Welcome to a new Terraform blog post series, **[Terraform ERRORS!](https://dev.to/pwd9000/series/29961)** In this series, we will explore common errors and issues that you may encounter when working with Terraform and how to resolve them.  

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

**Cause:** In a real world scenarios, this violation can happen when the role assignment was created outside of Terraform, for example by an **Operations** or **Security** team, or by **Azure Policy** to enforce certain security or operational conditions, or perhaps the permission was set as part of a previous different Terraform configuration with a separate state file. So when our current Terraform configuration tries to create the role assignment again, it fails as the permission already exists.  

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

### **Solution 2:** Use the Terraform `import` block

If you want to take over the management of an existing permission using terraform that was created outside of **Terraform**, you can use the `import` block to import the existing role assignment into Terraform's state file. This way you can avoid the violation by importing the existing role assignment into Terraform's state file and manage it from there.  

Now the tricky part. Sadly at the writing of this post there is no `data` source for `azurerm_role_assignment` to check if the role assignment already exists before creating it. So we need to use the `import` block to import the existing role assignment into Terraform's state file, so first we need to check what the existing role assignment ID/s are, that we want to import by using `az` CLI or the Azure Portal.  

```azurecli
# Log in to Azure
az login --tenant ${TENANT_ID}

# Get the object id of the user assigned identity (principal_id)
az identity show --name ${IDENTITY_NAME} --resource-group ${RESOURCE_GROUP_NAME} --query "{ObjectId:principalId}" -o tsv

# Get the ID/s of the existing role assignment/s (Resource level)
az role assignment list --assignee ${IDENTITY_NAME} --scope ${RESOURCE_ID} --query "[].id" -o tsv

# Get the ID/s of the existing role assignment/s (Resource Group level) ~ This is the one we want to import on this example ~
az role assignment list --assignee ${IDENTITY_NAME} --scope /subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP_NAME} --query "[].id" -o tsv

# Get the ID/s of the existing role assignment/s (Subscription level)
az role assignment list --assignee ${IDENTITY_NAME} --scope /subscriptions/${SUBSCRIPTION_ID} --query "[].id" -o tsv
```

Since we want to import the existing role assignment at the **Resource Group** level, the **Azure CLI** command `output` will be structured as follows:

```azurecli
/subscriptions/<SUB_ID>/resourcegroups/<RESOURCE_GROUP>/providers/Microsoft.Authorization/roleAssignments/<ROLE_ASSIGNMENT_NAME>
```

In this example we have 2 existing role assignments `Contributor` and `Reader` assigned at the `Resource Group` that we want to import into Terraform's state file.  

```bash
/subscriptions/829efd7e-aa80-4c0d-9c1c-7aa2557f8e07/resourceGroups/Demo-Inf-Dev-Rg/providers/Microsoft.Authorization/roleAssignments/1a533459-6925-4770-9c4e-0d341ae69691
/subscriptions/829efd7e-aa80-4c0d-9c1c-7aa2557f8e07/resourceGroups/Demo-Inf-Dev-Rg/providers/Microsoft.Authorization/roleAssignments/38e0ac0b-8342-40d9-ba29-7bfc16de6352
```

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/DevOps-Terraform-Idempotency/assets/rbac.png)

To do this we need to add the `import` block to the `azurerm_role_assignment` resource to import the existing role assignments into Terraform's state file.  

```hcl
# Create a locals map of the RBAC permissions on the Resource Group level
locals {
  role_assignments = {
    Reader      = "/subscriptions/829efd7e-aa80-4c0d-9c1c-7aa2557f8e07/resourceGroups/Demo-Inf-Dev-Rg/providers/Microsoft.Authorization/roleAssignments d5ee3efa-0ebe-44b7-a6ff-cdf1abc64418",
    Contributor = "/subscriptions/829efd7e-aa80-4c0d-9c1c-7aa2557f8e07/resourceGroups/Demo-Inf-Dev-Rg/providers/Microsoft.Authorization/roleAssignments/511b6d94-4d69-41bd-898d-1d6ce49a9834"
  }
}

import {
  for_each = local.role_assignments
  to       = azurerm_role_assignment.rbac[each.key]
  id       = each.value
}

# Create the azurerm_role_assignment resource importing the existing role assignments
resource "azurerm_role_assignment" "rbac" {
  for_each             = local.role_assignments
  principal_id         = azurerm_user_assigned_identity.uai.principal_id
  role_definition_name = each.key
  scope                = azurerm_resource_group.rg.id
}
```

As you can see in the example above, the **Terraform Plan** will use the `import` block to import the existing role assignments into Terraform's state file. This way we can avoid the violation by importing the existing role assignments into Terraform's state file and manage them from there. This method is useful when you want to import existing role assignments into Terraform's state file and manage them from there.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/DevOps-Terraform-Idempotency/assets/plan3.png)

**NOTE:** Once the role assignments are imported into Terraform's state file, you can remove or comment out the `import` block from the configuration as it is only needed to import the existing role assignments into Terraform's state file and can now be managed from a terraform configuration.  

---

### **Solution 3:** Use `null_resource` with a `local-exec` provisioner using `az` CLI to create the role assignment

In some cases you may not want to manage the existing role assignments in Terraform's state file, but you still want to create the role assignment conditionally. Thus another way to handle the violation is by using a `null_resource` with a `local-exec` provisioner to create role assignments. This way we can avoid the violation by creating the role assignment using `az` CLI only when needed. This method is useful when you want to create the role assignment conditionally and is more flexible as it can be used with multiple user assigned identities or multiple role definitions as using `az`.

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

In the example since we know that the `contributor` role already exists causing a violation, using `az` CLI, will inherently skip any existing RBAC/IAM permissions and only create the `reader` role assignment as per the example. This way we can avoid the violation by skipping existing assignments and creating missing ones we need. The only downside to this method is that it uses `az` CLI to create the role assignment which may not be available in all environments or may require additional setup on the build agent.  

As mentioned one downside to this method is that changes are made outside of Terraform and will not be persisted in the **Terraform State File**. This can lead to **Drift** and **State Confusion** if not managed properly.  

**IMPORTANT!:** When using `az` CLI like this you need to be aware that you will need a way for your agent to also authenticate to Azure and have the necessary permissions to create the role assignment. This can be done by setting the environment variables `ARM_CLIENT_ID`, `ARM_CLIENT_SECRET`, `ARM_TENANT_ID` and `ARM_SUBSCRIPTION_ID` on the build agent to use a service principal with the necessary permissions. As you can see from the command above, we are using a service principal to authenticate to Azure and create the role assignment.  

```azurecli
az login --service-principal --username $ARM_CLIENT_ID --password $ARM_CLIENT_SECRET --tenant $ARM_TENANT_ID --output none
az account set --subscription $ARM_SUBSCRIPTION_ID --output none
az role assignment create --assignee ${azurerm_user_assigned_identity.uai.principal_id} --role ${each.key} --scope ${azurerm_resource_group.rg.id}
```

If you are using GitHub Actions, you can set these environment variables in the GitHub Secrets and use them in your workflow.  

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/DevOps-Terraform-Idempotency/assets/github-secrets.png)

Federated tokens via OIDC or other methods can also be used to authenticate to Azure and create the role assignment using the `az` CLI in the `local-exec` provisioner. For more details on how to authenticate to Azure using the `az` CLI, see **[Authenticate Azure CLI](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli/?wt.mc_id=DT-MVP-5004771)**

![image.png](https://raw.githubusercontent.com/Pwd9000-ML/blog-devto/main/posts/2025/DevOps-Terraform-Idempotency/assets/azure-login.png)#

---

## Best Practices to Avoid Problems with Idempotency

1. **Import Existing Resources:** Add unmanaged resources to Terraform's state before applying changes. but in some cases, this may not be possible or practical due to the complexity of the resource or the number of resources or perhaps teams involved in managing them when it comes to the business. For example if RBAC is managed by **operations** or **security** teams.
2. **Add Conditions:** based on the data sources or variables to create resources conditionally.
3. **Ignore Unimportant Changes:** Use lifecycle rules to avoid unnecessary updates and changes.
4. **Limit Provisioners:** Only use `local-exec` provisioners for tasks Terraform can't handle natively or for last resort special cases.
5. **Plan Before Apply:** Always run `terraform plan` before applying your configuration. This step helps you preview the changes Terraform will make, ensuring they align with your expectations. For beginners, planning is especially critical as it can catch common issues like misconfigurations or unintended resource changes before they happen. It's a simple but powerful way to avoid surprises and maintain control over your infrastructure. Always run `terraform plan` to preview changes and catch potential issues early. But remember that the plan will not show any errors for certain violations or conditions, so you will need to check the apply output for the error message in these cases.
6. **Sync with Cloud State:** Use `terraform refresh` to update Terraform's state before applying changes.

---

## Conclusion

Idempotency makes **Terraform** a reliable tool for managing cloud infrastructure. By understanding common problems and using the strategies in this blog, you can avoid errors and keep your infrastructure predictable. Whether you're working on Azure RBAC or other setups, these tips will help you write better Terraform configurations. With careful planning and good practices, you can ensure that Terraform runs smoothly and efficiently every time.

**Have you faced idempotency problems in Terraform? Share your solutions in the comments!**

If you enjoyed this post and want to learn more about **Terraform** and **Azure**, check out my other Terraform Series **[Terraform Pro Tips](https://dev.to/pwd9000/series/16567)**.

### _Author_

Like, share, follow me on: :octopus: [GitHub](https://github.com/Pwd9000-ML) | :penguin: [X/Twitter](https://x.com/pwd9000) | :space_invader: [LinkedIn](https://www.linkedin.com/in/marcel-l-61b0a96b/)

{% user pwd9000 %}

<a href="https://www.buymeacoffee.com/pwd9000"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=pwd9000&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>
