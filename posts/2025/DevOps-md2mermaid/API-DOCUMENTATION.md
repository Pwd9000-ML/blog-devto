# Convert 2 Mermaid API

Transform Markdown outlines into beautiful Mermaid diagrams instantly. Perfect for documentation automation, workflow visualization, and mind mapping.

**Version:** 0.4.5  
**Host:** convert2mermaid.p.rapidapi.com  
**Category:** Text Processing / Diagram Generation

## 🚀 Quick Start

Transform your Markdown text into Mermaid diagrams with a single API call:

```bash
curl -X POST https://convert2mermaid.p.rapidapi.com/convert \
  -H "X-RapidAPI-Key: YOUR_RAPIDAPI_KEY" \
  -H "X-RapidAPI-Host: convert2mermaid.p.rapidapi.com" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{
  "markdown": "# Project\n- Planning\n- Development\n- Testing\n- Deployment",
  "diagram": "flowchart",
  "output_format": "json",
  "export": false
}
JSON
```

**Parameters**
- `markdown` *(required)* – Markdown outline to transform.
- `diagram` *(optional, default `flowchart`)* – One of the 14 supported diagram types.
- `output_format` *(optional, default `json`)* – Choose `json`, `txt`, or `svg`.
- `export` *(optional, default `false`)* – Set `true` to force a file download response.

## 📋 Features

- **14 Diagram Types:** Generate `flowcharts`, `mindmaps`, `sequence`, `state`, `ER`, `Gantt`, `Git graph`, `User Journey`, `Class`, `C4`, `Pie`, `Sankey`, `Timeline`, and `Quadrant` diagrams
- **Multiple Output Formats:** Get results as JSON (default), plain text (txt), or rendered SVG
- **File Export Option:** Download diagrams as files with proper Content-Disposition headers (v0.4.0+)
- **Improved SVG Rendering:** Enhanced Base64 encoding for better diagram rendering (v0.4.5+)
- **Simple Input:** Plain Markdown text with headers and bullet points
- **Deterministic Output:** Same input always produces same output (cacheable)
- **Fast Response:** Sub-second processing time
- **No External Dependencies:** Complete diagram generation without external services


## 🔐 Authentication

Include these headers in every request:

| Header | Description | Required |
|--------|-------------|----------|
| X-RapidAPI-Key | Your RapidAPI subscription key | ✅ Yes |
| X-RapidAPI-Host | convert2mermaid.p.rapidapi.com | ✅ Yes |
| Content-Type | application/json | ✅ Yes (POST only) |

## 📍 Endpoints

### Health Check
**GET** `/health`

Check API availability and status.

**Response Example:**
```json
{
  "ok": true
}
```

### Convert to Mermaid
**POST** `/convert`

Transform Markdown text into Mermaid diagram syntax.

**Request Body:**
```json
{
  "markdown": "string (required)",
  "diagram": "flowchart | mindmap | sequence | state | er | gantt | git | journey | class | c4 | pie | sankey | timeline | quadrant (optional, default: flowchart)",
  "output_format": "json | txt | svg (optional, default: json)",
  "export": "boolean (optional, default: false) - When true, returns downloadable file"
}
```

**Response:**

Format: `json` (default)
```json
{
  "mermaid": "string"
}
```

Format: `txt`
```
Plain text Mermaid diagram code
(Content-Type: text/plain)
```

Format: `svg`
```
Rendered SVG image
(Content-Type: image/svg+xml)
```

**File Export (NEW in v0.4.0):**

When `export: true` is included in the request, the response includes a `Content-Disposition` header that triggers a file download in browsers and clients. The filename format is:

`diagram-{diagram_type}-{YYYYMMDD-HHMMSS}.{extension}`

Examples:
- `diagram-flowchart-20251003-143022.txt`
- `diagram-mindmap-20251003-143030.json`
- `diagram-sequence-20251003-143045.svg`

This feature works with all 14 diagram types and all 3 output formats.

## 📊 Diagram Types

### Flowchart (default)
Creates a top-down flowchart with sequential connections.

**Input:**
```json
{
  "markdown": "# User Login Flow\n- Enter credentials\n- Validate input\n- Check database\n- Return token",
  "diagram": "flowchart"
}
```

**Output:**
```
flowchart TD;
N0["User Login Flow"];
N1["Enter credentials"];
N2["Validate input"];
N3["Check database"];
N4["Return token"];
N0-->N1;
N1-->N2;
N2-->N3;
N3-->N4;
```

**Rendered Result:**
Linear flow diagram connecting each step sequentially.

### Mindmap
Creates a radial mindmap with the first item as root.

**Input:**
```json
{
  "markdown": "# API Features\n- Authentication\n- Rate Limiting\n- Caching\n- Monitoring",
  "diagram": "mindmap"
}
```

**Output:**
```
mindmap
  API Features
    Authentication
    Rate Limiting
    Caching
    Monitoring
```

**Rendered Result:**
Central node "API Features" with four branches.

### Sequence
Creates a sequence diagram showing interactions between actors.

**Input:**
```json
{
  "markdown": "# Login Flow\n- User->System: Login request\n- System->Database: Check credentials\n- Database->System: Valid\n- System->User: Success",
  "diagram": "sequence"
}
```

**Output:**
```
sequenceDiagram
    User->System: Login request
    System->Database: Check credentials
    Database->System: Valid
    System->User: Success
```

**Rendered Result:**
Sequence diagram showing message flow between User, System, and Database.

**Format Guidelines:**
- Use `Actor->Target: Message` for interactions
- Use `Actor: Action` for single-actor actions
- Simple names are treated as participants

### State
Creates a state diagram showing state transitions.

**Input:**
```json
{
  "markdown": "# Order Processing\n- Pending\n- Confirmed\n- Shipped\n- Delivered",
  "diagram": "state"
}
```

**Output:**
```
stateDiagram-v2
    Pending --> Confirmed
    Confirmed --> Shipped
    Shipped --> Delivered
```

**Rendered Result:**
State diagram showing transitions from Pending through Delivered.

**Format Guidelines:**
- List states in sequential order
- States with spaces are automatically converted to underscores
- First item can be a descriptive title

### Entity Relationship (ER)
Creates an entity relationship diagram for database schemas.

**Input:**
```json
{
  "markdown": "# E-Commerce Schema\n- Customer\n- Order\n- Product\n- Customer ||--o{ Order : places\n- Order }|--|{ Product : contains",
  "diagram": "er"
}
```

**Output:**
```
erDiagram
    Customer {
    }
    Order {
    }
    Product {
    }
    Customer ||--o{ Order : places
    Order }|--|{ Product : contains
```

**Rendered Result:**
ER diagram showing Customer, Order, and Product entities with relationships.

**Format Guidelines:**
- Simple items create entities
- Use Mermaid ER syntax for relationships: `Entity ||--o{ OtherEntity : relationship`
- Supported cardinality: `||` (exactly one), `|{` (one or more), `o{` (zero or more)

### Gantt
Creates a Gantt chart for project planning and timelines.

**Input:**
```json
{
  "markdown": "# Project Plan\n- Phase 1:\n- Design\n- Planning\n- Phase 2:\n- Implementation\n- Testing",
  "diagram": "gantt"
}
```

**Output:**
```
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Phase 1
    Design : task, 2024-01-01, 7d
    Planning : task, 2024-01-01, 7d
    section Phase 2
    Implementation : task, 2024-01-01, 7d
    Testing : task, 2024-01-01, 7d
```

**Rendered Result:**
Gantt chart showing project phases and tasks.

**Format Guidelines:**
- Items ending with `:` create sections
- Other items become tasks
- Tasks are automatically assigned dates

### Git Graph
Creates a Git graph showing repository branching and merging.

**Input:**
```json
{
  "markdown": "# Git History\n- commit: Initial commit\n- branch develop\n- checkout develop\n- commit: Add feature\n- checkout main\n- merge develop",
  "diagram": "git"
}
```

**Output:**
```
gitGraph
    commit id: "Initial commit"
    branch develop
    checkout develop
    commit id: "Add feature"
    checkout main
    merge develop
```

**Rendered Result:**
Git graph showing branching and merging operations.

**Format Guidelines:**
- Use `commit: message` for commits
- Use `branch name` to create branches
- Use `checkout name` to switch branches
- Use `merge name` to merge branches

### User Journey
Creates a user journey diagram showing user interactions and satisfaction scores.

**Input:**
```json
{
  "markdown": "# Shopping Experience\n- Browse products: 5: Customer\n- Add to cart: 4: Customer\n- Checkout: 3: Customer, System\n- Payment: 2: Customer, Payment Gateway\n- Confirmation: 5: Customer",
  "diagram": "journey"
}
```

**Output:**
```
journey
    title User Journey
    Browse products: 5: Customer
    Add to cart: 4: Customer
    Checkout: 3: Customer, System
    Payment: 2: Customer, Payment Gateway
    Confirmation: 5: Customer
```

**Rendered Result:**
User journey showing satisfaction scores (1-5) for each step.

**Format Guidelines:**
- Format: `Task: score: actor1, actor2`
- Score ranges from 1 (poor) to 5 (excellent)
- Simple items default to score 5 with "User" actor

### Class
Creates a UML class diagram.

**Input:**
```json
{
  "markdown": "# Class Structure\n- Animal : +name\n- Animal : +age\n- Animal : +makeSound()\n- Dog : +breed\n- Cat : +color\n- Dog <|-- Animal\n- Cat <|-- Animal",
  "diagram": "class"
}
```

**Output:**
```
classDiagram
    class Animal
    Animal : +name
    Animal : +age
    Animal : +makeSound()
    class Dog
    Dog : +breed
    class Cat
    Cat : +color
    Dog <|-- Animal
    Cat <|-- Animal
```

**Rendered Result:**
UML class diagram showing inheritance and members.

**Format Guidelines:**
- Simple items create classes
- Use `ClassName : member` for attributes/methods
- Use `<|--`, `*--`, `o--` for relationships

### C4
Creates a C4 Context diagram for system architecture.

**Input:**
```json
{
  "markdown": "# System Architecture\n- User: End User\n- Frontend: Web Application\n- Backend: API Service\n- Database: PostgreSQL",
  "diagram": "c4"
}
```

**Output:**
```
C4Context
    title System Context
    Person(user0, "User", "End User")
    Person(user1, "Frontend", "Web Application")
    Person(user2, "Backend", "API Service")
    Person(user3, "Database", "PostgreSQL")
```

**Rendered Result:**
C4 Context diagram showing system components.

**Format Guidelines:**
- Format: `Component: Description`
- Simple items create system components
- Descriptions are optional

### Pie
Creates a pie chart for data visualization.

**Input:**
```json
{
  "markdown": "# Market Share\n- Product A : 45\n- Product B : 30\n- Product C : 15\n- Product D : 10",
  "diagram": "pie"
}
```

**Output:**
```
pie
    title Distribution
    "Product A" : 45
    "Product B" : 30
    "Product C" : 15
    "Product D" : 10
```

**Rendered Result:**
Pie chart showing percentage distribution.

**Format Guidelines:**
- Format: `Label : Value`
- Values can be absolute numbers (will be converted to percentages)
- Items without values default to 1

### Sankey
Creates a Sankey diagram showing flow between nodes.

**Input:**
```json
{
  "markdown": "# Energy Flow\n- Solar,Battery,50\n- Solar,Grid,30\n- Battery,Home,40\n- Grid,Home,60",
  "diagram": "sankey"
}
```

**Output:**
```
sankey-beta

Solar,Battery,50
Solar,Grid,30
Battery,Home,40
Grid,Home,60
```

**Rendered Result:**
Sankey diagram showing energy flow quantities.

**Format Guidelines:**
- Format: `Source,Target,Value` or `Source -> Target : Value`
- Values represent flow quantities
- Nodes are automatically created from sources and targets

### Timeline
Creates a timeline diagram showing events over time.

**Input:**
```json
{
  "markdown": "# Company History\n- 2010 : Company Founded\n- 2015 : Series A Funding\n- 2018 : Reached 1M Users\n- 2020 : IPO\n- 2023 : Global Expansion",
  "diagram": "timeline"
}
```

**Output:**
```
timeline
    title Timeline
    2010
        Company Founded
    2015
        Series A Funding
    2018
        Reached 1M Users
    2020
        IPO
    2023
        Global Expansion
```

**Rendered Result:**
Timeline showing chronological events.

**Format Guidelines:**
- Format: `Period : Event`
- Simple items can be periods or events
- Multiple events can be listed per period

### Quadrant
Creates a quadrant chart for prioritization matrices.

**Input:**
```json
{
  "markdown": "# Priority Matrix\n- High Priority: [0.8, 0.9]\n- Medium Priority: [0.5, 0.5]\n- Low Priority: [0.2, 0.3]\n- Review Later: [0.7, 0.2]",
  "diagram": "quadrant"
}
```

**Output:**
```
quadrantChart
    title Quadrant Chart
    x-axis Low --> High
    y-axis Low --> High
    High Priority: [0.8, 0.9]
    Medium Priority: [0.5, 0.5]
    Low Priority: [0.2, 0.3]
    Review Later: [0.7, 0.2]
```

**Rendered Result:**
2x2 matrix showing items plotted by coordinates.

**Format Guidelines:**
- Format: `Item: [x, y]`
- Coordinates range from 0.0 to 1.0
- Items without coordinates are auto-positioned

## 💻 Code Examples

### Python
```python
import requests

url = "https://convert2mermaid.p.rapidapi.com/convert"
headers = {
    "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",
    "X-RapidAPI-Host": "convert2mermaid.p.rapidapi.com",
    "Content-Type": "application/json"
}

# Example 1: Simple flowchart
data = {
    "markdown": "# Process\n- Start\n- Execute\n- Complete"
}
response = requests.post(url, json=data, headers=headers)
print(response.json()["mermaid"])

# Example 2: Mindmap
data = {
    "markdown": "# Product\n- Frontend\n- Backend\n- Database",
    "diagram": "mindmap"
}
response = requests.post(url, json=data, headers=headers)
print(response.json()["mermaid"])

# Example 3: Sequence diagram
data = {
    "markdown": "# Login\n- User->API: credentials\n- API->DB: verify\n- DB->API: success\n- API->User: token",
    "diagram": "sequence"
}
response = requests.post(url, json=data, headers=headers)
print(response.json()["mermaid"])

# Example 4: State diagram
data = {
    "markdown": "# Order States\n- Created\n- Paid\n- Shipped\n- Delivered",
    "diagram": "state"
}
response = requests.post(url, json=data, headers=headers)
print(response.json()["mermaid"])

# Example 4: Get plain text output (format: txt)
data = {
    "markdown": "# Deployment\n- Build\n- Test\n- Deploy",
    "diagram": "flowchart",
    "output_format": "txt"
}
response = requests.post(url, json=data, headers=headers)
print(response.text)  # Plain text Mermaid code

# Example 5: Get rendered SVG output (format: svg)
data = {
    "markdown": "# Components\n- Frontend\n- Backend\n- Database",
    "diagram": "mindmap",
    "output_format": "svg"
}
response = requests.post(url, json=data, headers=headers)
# Save SVG to file
with open('diagram.svg', 'w') as f:
    f.write(response.text)

# Example 6: Export as downloadable file (NEW in v0.4.0)
data = {
    "markdown": "# Deployment\n- Build\n- Test\n- Deploy",
    "diagram": "flowchart",
    "output_format": "txt",
    "export": True  # Triggers file download
}
response = requests.post(url, json=data, headers=headers)
# Response includes Content-Disposition header with filename
# e.g., diagram-flowchart-20251003-143022.txt
filename = response.headers.get('content-disposition', '').split('filename=')[1]
with open(filename, 'w') as f:
    f.write(response.text)
print(f"Saved as {filename}")
```

### JavaScript / Node.js
```javascript
const axios = require('axios');

const options = {
  method: 'POST',
  url: 'https://convert2mermaid.p.rapidapi.com/convert',
  headers: {
    'X-RapidAPI-Key': 'YOUR_RAPIDAPI_KEY',
    'X-RapidAPI-Host': 'convert2mermaid.p.rapidapi.com',
    'Content-Type': 'application/json'
  },
  data: {
    markdown: '# Workflow\n- Design\n- Implement\n- Test\n- Deploy',
    diagram: 'flowchart'
  }
};

axios.request(options)
  .then(response => console.log(response.data.mermaid))
  .catch(error => console.error(error));

// Example 2: Get TXT format
const txtOptions = {
  method: 'POST',
  url: 'https://convert2mermaid.p.rapidapi.com/convert',
  headers: {
    'X-RapidAPI-Key': 'YOUR_RAPIDAPI_KEY',
    'X-RapidAPI-Host': 'convert2mermaid.p.rapidapi.com',
    'Content-Type': 'application/json'
  },
  data: {
    markdown: '# API\n- Request\n- Process\n- Response',
    diagram: 'sequence',
    format: 'txt'
  }
};

axios.request(txtOptions)
  .then(response => {
    // Plain text Mermaid code
    console.log(response.data);
  })
  .catch(error => console.error(error));
```

### PHP
```php
<?php
$curl = curl_init();

curl_setopt_array($curl, [
  CURLOPT_URL => "https://convert2mermaid.p.rapidapi.com/convert",
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_POST => true,
  CURLOPT_POSTFIELDS => json_encode([
    "markdown" => "# Steps\n- First\n- Second\n- Third",
    "diagram" => "flowchart"
  ]),
  CURLOPT_HTTPHEADER => [
    "X-RapidAPI-Key: YOUR_RAPIDAPI_KEY",
    "X-RapidAPI-Host: convert2mermaid.p.rapidapi.com",
    "Content-Type: application/json"
  ],
]);

$response = curl_exec($curl);
curl_close($curl);
echo $response;
?>
```

### Go
```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

func main() {
    url := "https://convert2mermaid.p.rapidapi.com/convert"
    
    payload := map[string]string{
        "markdown": "# Task\n- Step 1\n- Step 2\n- Step 3",
        "diagram":  "flowchart",
    }
    
    jsonData, _ := json.Marshal(payload)
    req, _ := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
    
    req.Header.Add("X-RapidAPI-Key", "YOUR_RAPIDAPI_KEY")
    req.Header.Add("X-RapidAPI-Host", "convert2mermaid.p.rapidapi.com")
    req.Header.Add("Content-Type", "application/json")
    
    client := &http.Client{}
    resp, _ := client.Do(req)
    defer resp.Body.Close()
    
    var result map[string]string
    json.NewDecoder(resp.Body).Decode(&result)
    fmt.Println(result["mermaid"])
}
```

## 🎯 Use Cases

### 1. Documentation Automation
Convert README sections into visual diagrams:
```json
{
  "markdown": "# Installation\n- Clone repository\n- Install dependencies\n- Configure environment\n- Run application"
}
```

### 2. Project Planning
Visualize project structure:
```json
{
  "markdown": "# MVP Features\n- User Authentication\n- Data Storage\n- API Gateway\n- Frontend UI",
  "diagram": "mindmap"
}
```

### 3. Process Workflows
Document business processes:
```json
{
  "markdown": "# Order Processing\n- Receive order\n- Validate payment\n- Check inventory\n- Ship product\n- Send confirmation"
}
```

### 4. Learning Paths
Create educational roadmaps:
```json
{
  "markdown": "# Learn Python\n- Basics\n- Data Structures\n- OOP\n- Web Development\n- Machine Learning",
  "diagram": "mindmap"
}
```

### 5. API Interactions
Document API request/response flows:
```json
{
  "markdown": "# API Call Flow\n- Client->API: POST /users\n- API->Database: INSERT user\n- Database->API: user_id\n- API->Client: 201 Created",
  "diagram": "sequence"
}
```

### 6. Application States
Model application lifecycle:
```json
{
  "markdown": "# App Lifecycle\n- Initializing\n- Running\n- Paused\n- Stopped",
  "diagram": "state"
}
```

### 7. Database Design
Visualize database schemas:
```json
{
  "markdown": "# Blog Schema\n- User\n- Post\n- Comment\n- User ||--o{ Post : writes\n- Post ||--o{ Comment : has",
  "diagram": "er"
}
```

### 8. Project Timelines
Create Gantt charts for project management:
```json
{
  "markdown": "# Sprint Planning\n- Phase 1:\n- Requirements\n- Design\n- Phase 2:\n- Development\n- Testing",
  "diagram": "gantt"
}
```

### 9. Version Control History
Visualize Git branching and merging:
```json
{
  "markdown": "# Release Flow\n- commit: Initial release\n- branch hotfix\n- checkout hotfix\n- commit: Bug fix\n- checkout main\n- merge hotfix",
  "diagram": "git"
}
```

### 10. Customer Experience Mapping
Track user satisfaction through journey:
```json
{
  "markdown": "# Onboarding\n- Sign up: 5: User\n- Verify email: 4: User\n- Complete profile: 3: User\n- First purchase: 5: User",
  "diagram": "journey"
}
```

### 11. Software Architecture
Document class hierarchies:
```json
{
  "markdown": "# Payment System\n- Payment : +amount\n- Payment : +process()\n- CreditCard\n- PayPal\n- CreditCard <|-- Payment\n- PayPal <|-- Payment",
  "diagram": "class"
}
```

### 12. System Architecture
Create C4 diagrams for system context:
```json
{
  "markdown": "# Microservices\n- User: Customer\n- API: Gateway Service\n- Auth: Authentication Service\n- DB: Database Cluster",
  "diagram": "c4"
}
```

### 13. Data Distribution
Show proportional data with pie charts:
```json
{
  "markdown": "# Revenue Sources\n- Subscriptions : 60\n- Ads : 25\n- Partnerships : 15",
  "diagram": "pie"
}
```

### 14. Flow Analysis
Visualize resource flows with Sankey:
```json
{
  "markdown": "# Traffic Sources\n- Google,Website,5000\n- Social,Website,3000\n- Website,Signup,2000\n- Website,Purchase,1500",
  "diagram": "sankey"
}
```

### 15. Historical Events
Display chronological timelines:
```json
{
  "markdown": "# Product Evolution\n- 2020 : Beta Launch\n- 2021 : Public Release\n- 2022 : Enterprise Edition\n- 2023 : Global Expansion",
  "diagram": "timeline"
}
```

### 16. Priority Matrices
Create 2x2 prioritization charts:
```json
{
  "markdown": "# Task Priority\n- Fix Critical Bug: [0.9, 0.9]\n- New Feature: [0.7, 0.6]\n- Refactoring: [0.3, 0.4]\n- Documentation: [0.2, 0.5]",
  "diagram": "quadrant"
}
```

## 📤 Output Formats

### JSON Format (default)
Returns Mermaid diagram code as JSON for programmatic processing.

**Example Request:**
```json
{
  "markdown": "# Process\n- Start\n- Execute\n- Complete",
  "diagram": "flowchart",
  "output_format": "json"
}
```

**Response:**
```json
{
  "mermaid": "flowchart TD;\nN0[\"Process\"];\nN1[\"Start\"];\nN2[\"Execute\"];\nN3[\"Complete\"];\nN0-->N1;\nN1-->N2;\nN2-->N3;"
}
```

### TXT Format
Returns plain text Mermaid diagram code that can be copied directly into Mermaid tools.

**Example Request:**
```json
{
  "markdown": "# Process\n- Start\n- Execute\n- Complete",
  "diagram": "flowchart",
  "output_format": "txt"
}
```

**Response (text/plain):**
```
flowchart TD;
N0["Process"];
N1["Start"];
N2["Execute"];
N3["Complete"];
N0-->N1;
N1-->N2;
N2-->N3;
```

**Use Cases:**
- Copy-paste into <a href="https://mermaid.live">Mermaid Live Editor</a>
- Save as `.mmd` file for version control
- Direct integration with documentation tools
- Manual editing and customization

### SVG Format
Returns rendered SVG diagram ready for embedding in web pages.

**Example Request:**
```json
{
  "markdown": "# Process\n- Start\n- Execute\n- Complete",
  "diagram": "flowchart",
  "output_format": "svg"
}
```

**Response (image/svg+xml):**
```xml
<svg xmlns="http://www.w3.org/2000/svg" ...>
  <!-- Rendered Mermaid diagram -->
</svg>
```

**Use Cases:**
- Direct embedding in HTML/web pages
- Email newsletters and reports
- PDF generation
- Image previews without JavaScript

**Rendering Notes:**
- SVG diagrams are rendered server-side by the API
- All 14 diagram types supported
- High-quality vector graphics output
- No client-side JavaScript required

### File Export (NEW in v0.4.0)
Enable file downloads by setting `export: true` in your request. This adds a `Content-Disposition` header to the response, triggering automatic file downloads in browsers and making it easy to save diagrams.

**Example Request:**
```json
{
  "markdown": "# Process\n- Start\n- Execute\n- Complete",
  "diagram": "flowchart",
  "output_format": "txt",
  "export": true
}
```

**Response Headers:**
```
Content-Type: text/plain; charset=utf-8
Content-Disposition: attachment; filename=diagram-flowchart-20251003-143022.txt
```

**Filename Format:**
`diagram-{diagram_type}-{YYYYMMDD-HHMMSS}.{extension}`

**Supported Combinations:**
- `output_format: "json"` + `export: true` → Downloads as `.json` file
- `output_format: "txt"` + `export: true` → Downloads as `.txt` file  
- `output_format: "svg"` + `export: true` → Downloads as `.svg` file

**Use Cases:**
- Automated diagram archival systems
- Bulk diagram generation and storage
- User-friendly download buttons in web interfaces
- Integration with file management systems
- Direct save to local filesystem in scripts

**Backward Compatibility:**
When `export: false` (default) or omitted, responses return as standard HTTP responses without file download headers, maintaining compatibility with existing integrations.

## 🔧 Input Format Guidelines

### Supported Markdown Elements
- **Headers:** `#`, `##`, `###` (treated as items)
- **Bullet Points:** `-`, `*`, `+` (treated as items)
- **Plain Text:** Any non-empty line (treated as items)

### Example Input Patterns
```markdown
# Main Topic
- Sub item 1
- Sub item 2
  
## Section Header
* Point A
* Point B

Plain text line
Another plain line
```

## ⚠️ Error Handling

### Status Codes
| Code | Description | Action |
|------|-------------|--------|
| 200 | Success | Process the mermaid output |
| 400 | Bad Request | Check JSON syntax |
| 401 | Unauthorized | Verify API key |
| 422 | Validation Error | Check field names (use "diagram" not "diagram_type") |
| 429 | Rate Limit | Reduce request frequency |
| 500 | Server Error | Retry with exponential backoff |

## 📈 Rate Limits & Pricing

### Pricing Tiers

| Tier | Monthly Price | Included Calls | Overage Cost | Rate Limit |
|------|---------------|----------------|--------------|------------|
| **Free** | $0 | 100/month (~3/day) | N/A | 5 req/min |
| **Pro** | $5.99 | 5,000/month (~166/day) | $0.004/call | 30 req/min |
| **Ultra** | $29 | 25,000/month (~833/day) | $0.002/call | 60 req/min |
| **Mega** | $99 | 500K+/month | N/A | 500+ req/min |

### Rate Limiting Details
- **Per-minute limits:** Enforced per IP address on 60-second rolling window
- **Monthly quotas:** Tracked by your RapidAPI subscription
- **Burst Protection:** HTTP 429 returned when rate limit exceeded
- **Retry Strategy:** Implement exponential backoff when hitting limits

### Choosing the Right Plan
- **Free:** Testing, evaluation, hobby projects (100 calls/month)
- **Pro:** Small businesses, production apps (5K calls/month)
- **Ultra:** Growing businesses, high-traffic applications (25K calls/month)
- **Mega:** Large enterprises, high-volume integrations (500K+ calls/month)

### Usage Monitoring
Track your consumption and upgrade/downgrade anytime via RapidAPI dashboard at [https://rapidapi.com/pwd9000ml/api/convert2mermaid](https://rapidapi.com/pwd9000ml/api/convert2mermaid)

## 🔄 Versioning

Current version: **0.4.5**

### Changelog

**v0.4.5** (Latest)
- 🔧 Improved SVG rendering with proper Base64 encoding
- 🎨 Enhanced Mermaid syntax generation (removed semicolons, added indentation)
- 🐛 Better compatibility with modern Mermaid.js versions
- 📦 Server-side rendering for all diagram types
- ⚡ Faster SVG generation with optimized processing

**v0.4.0**
- 📥 Added `export` parameter for downloadable file responses
- 🗂️ File downloads include Content-Disposition headers with timestamped filenames
- 📝 Filename format: `diagram-{type}-{YYYYMMDD-HHMMSS}.{extension}`
- ✅ Works with all 14 diagram types and all 3 output formats (JSON, TXT, SVG)
- 📦 Backward compatible - existing integrations continue to work unchanged

**v0.3.0**
- ✨ Added `output_format` parameter with support for `json`, `txt`, and `svg` output formats
- 🎨 TXT format for direct copy-paste into Mermaid tools
- 🖼️ SVG format for rendered diagrams ready for embedding
- 📦 Backward compatible - existing integrations continue to work

**v0.2.0**
- ✨ Added support for 14 diagram types (Gantt, Git, Journey, Class, C4, Pie, Sankey, Timeline, Quadrant)
- 📊 Enhanced ER, State, and Sequence diagram support

**v0.1.0**
- 🎉 Initial release with Flowchart and Mindmap support

The API maintains backward compatibility. New features are added as optional parameters.

## 💡 Pro Tips

1. **Cache Results:** Outputs are deterministic - cache them to reduce API calls
2. **Choose the Right Format:** 
   - Use `json` for programmatic processing and API integrations
   - Use `txt` for copy-paste into Mermaid Live Editor or manual editing
   - Use `svg` for direct embedding in web pages and documents
3. **Use Export for Downloads:** Set `export: true` when you need to save diagrams as files (v0.4.0+)
4. **Batch Processing:** Process multiple diagrams in parallel (respect rate limits)
5. **Error Handling:** Implement retry logic with exponential backoff for 429/500 errors
6. **Validation:** Validate JSON before sending to avoid 422 errors
7. **Monitoring:** Track your usage via RapidAPI dashboard
8. **SVG for Production:** SVG format is ideal for production use with server-side rendering

### Test Coverage

The API includes comprehensive test coverage:
- Unit tests for all 14 diagram types
- Integration tests for all output formats (JSON, TXT, SVG)
- Export functionality tests
- RapidAPI authentication tests

## 🆘 Support

- **RapidAPI Hub:** [https://rapidapi.com/Pwd9000ML/api/convert2mermaid/discussions](https://rapidapi.com/Pwd9000ML/api/convert2mermaid/discussions)


## 📚 Additional Resources

- **Mermaid.js Documentation:** [https://mermaid.js.org/](https://mermaid.js.org/)
- **Mermaid Live Editor:** [https://mermaid.live](https://mermaid.live)
- **API Status:** Monitor via RapidAPI dashboard

## 📝 License & Terms

Usage is subject to:
- RapidAPI Terms of Service
- Your subscription plan limits
- Fair use policy to prevent abuse

---

**Ready to transform your Markdown into beautiful diagrams?**

🚀 [Subscribe on RapidAPI](https://rapidapi.com/Pwd9000ML/api/convert2mermaid)
