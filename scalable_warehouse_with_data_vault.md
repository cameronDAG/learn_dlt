# Chapter 1 - INTRODUCTION TO DATA WAREHOUSING
## Information Hierarchy
![information_hierarchy](hierarchy.png)


- Data: Raw facts without context.
- Information: Organized data with relevance and purpose.
- Knowledge: Synthesized information enriched by experience.
- Wisdom: Applied knowledge in novel or complex situations.

## History of Data Warehousing
### Decision Support Systems
a DSS is comprised of an analytical models database that is fed with selected data extracted from source systems. The raw data is aggregated within the analytical models database or on the way into the system.

### Data Warehouse Systems
The data warehouse provides nonvolatile, subject-oriented data that is integrated and consistent to business users on all targeted levels. Subject orientation differs from the functional orientation of an ERP or operational system by the focus on a subject area for analysis.


The integration of the various data sources within or external to the organization is performed on the business keys in many cases. This becomes a problem if a business object, such as a customer, has different business keys in each system. Which is why on the next part we're talking about the new solution: EDW.

### Enterprise Data Warehouse (EDW)
Instead of focusing on a single subject area for analysis, an enterprise data warehouse tries to represent all of an organization’s business data and its business rules. The data in the warehouse is then presented in a way that all required subject areas are available to business users.

#### Key Features of EDW
- Access: Fast, intuitive, and meaningful data access for users.
- Multiple Subject Areas: Tailored data marts for different departments.
- Single Version of Truth: Unified, validated data across the organization.
- Single Version of Facts: Complete raw data retained for compliance and auditing.

#### Technical and Strategic Requirements
- Mission Criticality: EDWs are vital for strategic decisions and operational support.
- Scalability: Must handle growing data volumes and user demands.
- Big Data: Must manage volume, velocity, and variety of data.
- Performance: Efficient data loading and query response times are crucial.
- Complexity: Challenges in sourcing, transforming, and loading data.
- Auditing & Compliance: Traceability of data sources and processes is essential.
- Cost Management: Includes storage, quality, planning, and adaptability to changing requirements.

## Data Vault 2.0
- Modeling: Optimized for performance and scalability.
- Methodology: Agile and Scrum-based practices.
- Architecture: Supports NoSQL and big data systems.
- Implementation: Automated and pattern-based for efficiency.

## Data Warehouse Architecture
### 2-Layers model
![2_layers](2_layers.png)


Layers:
- Staging
- Dimensional Data Marts


The raw data from the source systems is loaded into the stage area. The goal is to have an exact copy of all data that should be loaded into the data warehouse. Once the data has been loaded to the stage area, the data will be loaded into the data warehouse.


The advantage of a two-layered architecture is that it is easy to build a dimensional store from the source data as compared to other architecturess. However, the disadvantage is that it is more complex to build a second dimensional model from the same source data because the data needs to be loaded again from the staging. It is not possible to reuse existing ETL packages


### 3-Layers model
![3_layers](3_layers.png)


Layers:
- Staging
- ODS/EDW (normalized)
- Dimensional Data Marts


The staging area temporarily stores raw data extracted from various source systems. The data warehouse holds raw data modeled in a third-normal form. It integrates all data of the enterprise, but is still based on physical tables from the source systems. On top of the normalized view of the business data, there is a dimensional model. Business users can access and analyze the data using subject-oriented data marts.

# Chapter 2 -SCALABLE DATA WAREHOUSE ARCHITECTURE
Best approach = Cycle/Sprint over Big Bang

## Dimension of Scalable Warehouse Architecture
### Workload
Growing data volumes and user concurrency require parallel processing (MPP/SMP).

### Data Complexity
Following factors contributing to the growth of data complexity:
- Variety of data
- Volume of data
- Velocity of data
- Veracity (trustworthiness) of data

### Analytical Complexity
Due to the availability of large volumes of data with high velocity and variety, businesses demand different and more complex analytical tasks to produce the insight required to solve their business problems. Some of these analyses require that the data be prepared in a fashion not foreseen by the original data warehouse developers.

### Query Complexity
SQL optimization and performance tuning are critical for large-scale queries.

### Availability
SLAs require high uptime; solutions include clustering and parallel data loads. The availability of a data warehouse system might be affected by added functionality. One example is the addition of new data sources that have to be loaded and integrated into a new data mart. This, however, would extend the time needed to load all data sources and build the data marts.

### Security
Larger, diverse datasets need robust governance and protection mechanisms.

## Data Vault 2.0 Architecture
The Data Vault 2.0 architecture addresses the extensibility and dimensions of scalability by modifying a typical three-layer data warehouse architecture [3_layers_model](#3-layers-model)


Here's the modification:
- A staging area which does not store historical information and does not apply any changes to the data, except ensuring the expected data type.
- A data warehouse layer modeled after the Data Vault modeling technique.
- One or more information mart layers that depend on the data warehouse layer.
- An optional Metrics Vault that is used to capture and record runtime information.
- An optional Business Vault that is used to store information where the business rules have been applied. In many cases, the business rules change or alter the data when transforming it into useful information.
- An optional Operational Vault that stores data fed into the data warehouse from operational systems.
- Capabilities for managed self-service BI.

### Business Rules
#### Definition
Generally stated, business rules modify the incoming data to fit the requirements of the business.Hard business rules are the technical rules that align the data domains, so-called data type matching. As a rule of thumb, hard business rules never change the meaning of the incoming data, only the way the data is stored. Opposite from hard business rules, soft business rules enforce the business requirements that are stated by the business user. These business rules change the data or the meaning of the data.

#### Application
In data warehousing, business rules can be divided into hard rules, which enforce technical constraints such as data types and must be applied in the staging area, and soft rules, which transform or interpret data to fit business requirements. Traditional two- and three-layer architectures often apply both types of rules early in the ETL process, which creates heavy dependencies and makes adapting to changing business rules complex and costly. Data Vault 2.0 addresses this by separating hard and soft rules: only hard rules are enforced during loading, while soft rules are deferred to the information mart layer. This approach preserves historical data, avoids breaking ETL jobs when business rules change, and provides greater flexibility, scalability, and adaptability for evolving business needs.

### Staging Area Layers
The staging layer is used when loading batch data into the data warehouse. Its primary purpose is to extract the source data as fast as possible from the source system in order to reduce the workload on the operational systems. In addition, the staging area allows the execution of SQL statements against the source data, which might not be the case with direct access to flat files, such as CSV files or Excel sheets.

### Data Warehouse Layer
The second layer in the Data Vault 2.0 architecture is the data warehouse, the purpose of which is to hold all historical, time-variant data. The data warehouse holds raw data, not modified by any business rule other than hard business rules. Therefore, the data is stored in the granularity as provided by the source systems. The data is nonvolatile and every change in the source system is tracked by the Data Vault structure.

### Information Mart Layer
Typically, the end-user accesses only the information mart which provides the data in a way that the end-user feels most comfortable with. The information in the information mart is subject oriented and can be in aggregated form, flat or wide, prepared for reporting, highly indexed, redundant and quality cleansed.

### Metrics Vault
The Metrics Vault is used to capture and record runtime information, including the run history, process metrics, and technical metrics, such as CPU loads, RAM usage, disk I/O metrics and network throughput.

### Business Vault
The Business Vault is a sparsely modeled data warehouse based on Data Vault design principles, but houses business-rule changed data. In other words, the data within a Business Vault has already been changed by business rules. 

### Operational Vault
The Operational Vault is an extension to the Data Vault that is directly accessed by operational systems  There are occasions when such systems need to either retrieve data from the enterprise data warehouse or when they need to write data back to it. Examples include master data management (MDM) systems, such as Microsoft Master Data Services (MDS) or metadata management systems. In both cases, there is an advantage of directly operating on the data warehouse layer instead of using an information mart or staging area. Other cases include data mining applications that directly analyze the raw data stored within the data warehouse layer. Often, whenever the interfacing application requires real-time support, whether reading or writing, direct access to the Operational Vault is the best option.

### Managed Self-service BI
An approach called self-service BI allows end-users to completely circumvent IT due to its unresponsiveness. In this approach, business users are left on their own with the whole process of sourcing the data from operational systems, integration, and consolidation of the raw data.

But, of course there's many setbacks to this approach, including:
- Direct access to source systems: end-users should not directly access the data from source systems.
- Unintegrated raw data: when sourcing data from multiple source systems, business users are left alone with raw data integration. This can become a tedious and error-prone task if performed manually
- Low data quality: data from source systems often have issues regarding the data quality.
- Unconsolidated raw data: in order to analyze the data from multiple source systems, the data often requires consolidation. Without this consolidation, the results from business analysis will be meaningless.
- Nonstandardized business rules: because end-users are dealing with only the raw data in self-service BI, they have to implement all business rules that transform the raw data into meaningful information.

# Chapter 3 - THE DATA VAULT 2.0 METHODOLOGY
## Project Planning
- Alpha Release: distributed to technical business analysts. The data here has not have any business rules yet
- Beta Release:  has been tested thoroughly by IT and business representatives and no longer contains any obvious or known errors.
- Gamma Release: using a more user-friendly schema and is made available to all business users.

### Capability Maturity Model Integration
a process improvement framework that has been developed to address a broad range of application environments. There are three different models based on the CMMI framework.

- CMMI for Development, a process model for process management and improvement in software development organizations.
- CMMI for Acquisition, a model for organizations that have to initiate and manage the acquisition of products and services
- CMMI for Services, a process model for organizations to help them to deploy and manage services

#### Capability Level
- Level 0(Incomplete): It indicates that processes are not, or only partially, performed. It also indicates that at least one specific goal of the process area is not satisfied.
- Level 1(Performed): if all generic goals of level 1 are satisfied. This level requires that processes are performed and produce the needed output. However, this level doesn’t require that the process itself be institutionalized, which means that process improvements can be lost over time.
- Level 2(Managed): requires a process that is planned and executed in accordance with policy. All relevant stakeholders are involved in the process, which is monitored, controlled, reviewed and evaluated on a regular basis
- Level 3(Defined): It is characterized by a defined process which is a managed process derived from the organization’s set of standard processes and derived to the needs of the circumstances.
- Level 4(Quantitively Managed): A defined process (see capability level 3) that uses statistical and other quantitative methods to control selected subprocesses.
- Level 5(Optimizing): Focuses on the institutionalizing of an optimizing process.

#### Maturity Level
- Level 1(Initial): Indicates an organization with ad-hoc and chaotic processes. There is no stable process environment provided by the organization.
- Level 2(Managed): Have processes that are planned and executed in  accordance with policy and that involve all relevant stakeholders.
- Level 3(Defined): Indicates well-characterized and understood processes which are described in standards, procedures, tools, and methods
- Level 4(Quantitively Managed): Organizations use quantitative objectives for quality and process performance for managing their projects
- Level 5(Optimizing): Continually improve their processes using a quantitative approach to understand the variation of their processes and their process outcomes. 

### Integrating CMMI In the Data Vault 2.0 Methodology
- Measurable: will describe how the estimation process in the Data Vault 2.0 methodology is based on the comparison of estimated and actual effort.
- Repeatable: Repeatable processes.
- Defined: Promotes defined standards, rules, procedures and prebuilt templates, including project documentation. 
- Flexible
- Scalable
- Monitored: Consistent team reviews as in Scrum and constant releases in each sprint make sure that business users don’t lose interest in the project and its activities.
- Governed
- Optimized

### Managing the Project
#### Scrum
Waterfall approach. If everything goes well (and as planned), the waterfall approach is the most efficient way to carry out a project. However, it is almost impossible to carry out larger projects where the customer is not very concrete with requirements and ideas and where the business requirements evolve over time.

#### Iterative Approach
The previous section has already discussed that Scrum uses an iterative approach for developing the final system. Each iteration is a small step towards the final solution and adds more value to the product.

#### Product and Sprint Backlog
User requirements are maintained as user stories in a product backlog in Scrum. They are prioritized by business value and include requirements regarding customer requests, new features, usability enhancements, bug fixes, performance improvements, re-architecting, etc. 


User stories describe features from a user’s perspective and are kept in the product backlog until a team member selects a user story for implementation. The user stories are implemented in iterations called “sprints” which last usually two to four weeks. At the beginning of the project, user stories tend to be more general, roughly describing the primary features of the business users. 

### Defining the Project
There's 2 common objections in this stage: don't implement all tables from a source to keep the costs of integrating source systems low and don't be afraid touch the target multiple times in order to implement the final solution.

1st objection reasoning:
- Avoid expensive ETL and Infrastructure


2nd objection reasoning:
- Delivering small feature for each sprint is much safer

#### Agile Requirements Gathering
- Identify the required data
- Produce raw mart
- Produce raw report
- Gather business rules and other requirements
- Translate business rules and other requirements

### Estimation of the Project
#### Function Point Analysis
The functional characteristics of software are made up of external inputs (EI), which is the data that is entering a system; external outputs (EO) and external inquiries (EQ), which is data that leaves the system one way or another; internal logical files (ILF), which is data manufactured and stored within the system; external interface files (EIF), which is data that is maintained outside the system but necessary to perform the task.

#### Measuring with Function Point
- determine function point count type.
- identify the counting boundary
- identify and count data function types
- identify and count transactional function types
- determine unadjusted function point count
- determine value adjustment factor
- calculate final adjusted function point count



![function_point](function_point.png)

## Project Execution
1. Envision initial architecture
2. Model details just-in-time
3. Prove architecture early
4. Focus on usage
5. Avoid focusing on “the one truth”
6. Organize work by requirements
7. Active stakeholder participation

### Traditional SDLC
#### Requirements Engineering
- Business area	data requirements
- Architecture requirements
- Audit	requirements
- Archive requirements

#### Design
During the design phase, the data warehouse designers design the architecture of the data warehouse, such as the layers and each module of the system. The definition is based on the “Data Warehouse Definition” document and includes the database definitions of each layer, such as the structure of the staging area tables, the tables in the data warehouse layer and the star schema in the data mart.

#### Implementation and Unit Testing
Once the data warehouse has been described (in the requirements engineering phase) and designed (in the design phase), the individual modules of the system are implemented by the data warehouse developers. While they develop the modules, they also test the modules and remove errors found in this process.

#### Integration and System Testing
The individual units are connected to each other and integrated. This integration process starts with some modules at the bottom of the architecture which are fully integrated and tested.

#### Operation and Maintenance
In the last phase of the waterfall model, the data warehouse is handed over to operations where the system is installed at the end-user premises for regular use. If end-users find bugs in the data  warehouse, the operations team is responsible for correcting those bugs and handling other modifications of the data warehouse. This continuous process is performed until the data warehouse retires or is replaced by a new data warehouse

## Review and Improvement
### Six Sigma
![six_sigma](6_sigma.png)

- DMAIC (Define – Measure – Analyze – Improve – Control) -> fix existing process
- DMADV (Define – Measure – Analyze – Design – Verify) -> create new product with high standard

In this implementation, we use DMAIC
1. define the problem and clearly describe the impact on customer satisfaction stakeholder’s employees, and profitability.
2. measure the current performance to identify opportunities for improvement.
3. search for the root cause during the analyze phase. Opportunities for improvement are prioritized by two dimensions: their contribution to customer satisfaction and the impact on profitability.
4. The improvement step implements the opportunities identified in the previous step. Project members develop solution candidates and select the solution with the best results and performance.
5. The last step of DMAIC improvement is the control step. Its goal is to control the improved processes and to make sure that the Six Sigma initiative sustains.

### Total Quality Management
![data_quality](data_quality_dimension.png)


- Total Data Quality Management -> ensuring that data is fit for use and continuously improved, just like physical products in manufacturing.
- Data Warehouse Quality -> not only clean and reliable data, but also the performance, usability, and business value of the entire warehouse system.

# Chapter 4 -  DATA VAULT 2.0 MODELING
- hub -> separates the business keys from the rest of the model
- link -> stores relationships between business keys
- satellites -> store the context (the attributes of a business key or relationship)

### Hub Entities
When business users access information in an operational system, they use a business key to refer to the business objects. This might be a customer number, invoice number, or a vehicle identification number. 

### Link Entities
The Data Vault models these relationships with links that connect two or more hubs. Typical business processes are purchasing, manufacturing, advertising, marketing, and sales. Because these processes often (but not always) represent transactions, a link often represents a transaction as well. 

### Satellite Entities
The missing piece is the context of these business objects and the context of these links. For a flight transaction, this might be the air time of the plane or the security delay of a flight.

## Hub Definition
Hubs are defined using a unique list of business keys and provide a soft integration point of raw	data that is not altered from the source system, but is supposed to have the same semantic meaning. Therefore, business keys in the same hub should have the same semantic granularity.

### Business Key
Business keys are used to identify, track, and locate information. By definition, a business key should have a very low propensity to change and should be unique.

### Structure
1. Hash Key
2. Business Key
3. Load Date
4. Record Source
5. Last seen date

## Link Definition
The link entity type is responsible for modeling transactions, associations, hierarchies, and redefinitions of business terms. Links capture and record the past, present, and future relationships between data elements at the lowest possible granularity. 

Don’t put Begin/End dates directly in Links, doing so makes the model rigid and unable to capture multiple, temporary, or reversible changes. Instead: keep Links timeless, and capture timelines/context in Satellites.

### Structure
1. Hash Key
2. Load Date
3. Record Source
4. Last Seen Date
5. Dependent child key

## Satellite Definition
Satellites store all data that describes a business object, relationship, or transaction. They add context at a given time or over a time period to hubs and links. However, this context often changes in a business – thus the descriptive data in a satellite also changes over time. The purpose of a satellite is to track those changes as well.

### Splitting Satellite

#### By Source System
It is recommended practice to split the incoming data first by the source system. That means that each incoming data set is kept in individual satellites, which are in turn dependent on their parent (either a hub or link). 

#### By Rate of Change
Those attributes that are frequently changed are stored in one satellite, and those attributes that change less frequently are stored in another. If there are more than two frequencies, there	should be more than two satellites.

### Structure
1. Load Date
2. Record Source
3. Parent Hash Key
4. Load End Date
5. Extract Date
6. Hash diff

## Link Driving Key
Without the driving key concept, the hub entries would be completely independent from each other. The satellite entries would depend on these independent link entries, having nothing to do with each other. 

# Chapter 5 - INTERMEDIATE DATA VAULT MODELING
## Hub Application
### Business key consolidation
Since multi-source may have a multiple kind of business keys for the same entity, it is best to use same-as link that's stored at another hub. same-as link is a special link to record many business keys that are actually referring to the same entity.

## Link Application
- Don't use link-on-link, make them independent
- Same-as link
- Hierarchical links -> used to model parent-child hierarchies using Data Vault links.
- Nonhistorized links -> stored the supposedly non-updateable event
- Nondescriptive links -> links that doesn't have any satellite
- Computed aggregated links ->  removes one hub from a link and aggregates the data by the remaining relationships.
- Exploration links -> computed links that have been created for business reasons only. 

## Satellite Application
- Overloaded satellite -> dumping the multi-source data into 1 satellite 
- Multi-active satellite -> store multiple entries per parent key. However, these records don’t come from different sources, but from a denormalized data source
- Status tracking satellite -> load audit trails or data from change data capture (CDC) systems
- Effectivity satellite -> track the effectivity of a relationship between two business objects among other applications 
- Record tracking satellite -> trace the metadata of the data changes itself
- Computed satellite ->  storing computed data, which 
is data that is the result of aggregation, summarization, correction, evaluation, etc. It might be the outcome of data quality routines, cleansing routines or address correction routines.

# Chapter 6 - ADVANCED DATA VAULT MODELLING
## Point-in-Time Table
In Data Vault, hubs and satellites are separate. To get the “state of data at a certain time,” you usually need to join multiple satellites → this can be slow.


Makes historical queries easier and faster in a Data Vault. PIT table stores snapshot keys and timestamps, so queries can directly join PIT → satellite records.

### Structure
1. Hub ID
2. Load Date
3. Foreign key to the latest satellite records

## Bridge Table
Handles many-to-many relationships between hubs.

### Structure
1. Hub A ID
2. Hub B ID
3. Aggregated data (optional)

## Reference table
Stores static or rarely changing lookup data.

### No-History Reference table
The most basic reference table is just a typical table in third or second normal form. This basic table is used when there is no need to store history for the reference data. That is often the case for reference data that is not going to change or that will change very seldom.

### History-based Reference table
Using satellite connected to the reference table if it needed to be historized

# Chapter 7 - DIMENSIONAL MODELING
## Star Schemas
Using denormalized form of table. Structure including:
1. Fact Table: holds the measures of the business,
2. Dimension Table: group the facts into categories and provide additional descriptive attributes to these categories

## Multiple Stars
This behavior is supported by conformed dimensions, which are used by multiple stars (a fact table with its dimension tables) and therefore connect these individual stars via the conformed dimension itself.

## Dimension Design
### Slowly Changing Dimension
- Slowly changing dimension type 0: preserves the initial dimensional attribute values. If a change occurs in the source system, the value in the dimension is not changed.
- Slowly changing dimension type 1: The dimension’s attribute always reflects the most current value.
- Slowly changing dimension type 2: changes in the source system add a new row.
- Slowly changing dimension type 3: track history in additional columns.
- Slowly changing dimension type 4: this type puts volatile attributes into a separate mini-dimension table.
- Slowly changing dimension type 5: a hybrid between type 4 and type 1 dimensions (4 + 1 equals 5). It allows access of the currently assigned mini-dimension attributes along with the base dimension’s others without linking through a fact table.
- Slowly changing dimension type 6: this type adds current attributes to a type 2 dimension.
- Slowly changing dimension type 7: this type achieves the same functionality as type 6 dimensions but with dual foreign keys added to the fact table: one that references a type 2 dimension with the tracked attributes, while the other one references the current row.

### Hierarchies
They allow drilling down of data in order to analyze the data in more detail. Consider the following example: An Excel PivotTable presents worldwide passenger revenue of several years in total values. Each level of the hierarchy is based on one of the physical attributes of the dimension table.

### Snowflake Design
allows indirect dimension tables join. This is useful if the relationships between dimension attributes should be modeled explicitly. 

# Chapter 8 - PHYSICAL DATA WAREHOUSE DESIGN
Workload Characteristic:
1. Data latency
2. Consistency
3. Updateability
4. Data types
5. Response time
6. Predictability

## Seperate Environmnet for Development, Testing and Production
### Blue-Green Deployment
- Blue → the version currently live (production).
- Green → the new version (update/upgrade).


When the new version is ready, user traffic is switched from Blue → Green quickly. If something goes wrong, you can roll back immediately by redirecting traffic back to Blue.

## Physical Data Warehouse Architecture on Premise
- Data Size
- Volatility
- Number of business processes
- Number of users
- Nature of use
- Service level agreement

## Hardware Architecture and Databases
- Single Server
- Scalable Shared Databases ->  allow user of a read-only database in multiple server instances
- Massively parallel processing (MPP) -> allows the distribution of data to multiple nodes on the grid. 

### Storage options
- RAID-0 -> Splits (stripes) data across multiple disks.
- RAID-1 -> Data is duplicated (mirrored) on two or more disks.
- RAID-5 -> Data striped across disks, and parity distributed across all disks (no single parity disk).
- RAID-6 -> Like RAID 5, but with two parity blocks distributed across disks.

## Database option
### TempDB
system database used to store temporary objects and data.

### Partitioning
Partition is used when the data in a table or index becomes too large to manage by SQL Server 2014. If the data is too big, the performance of maintenance functions, such as backup or restore, can drop.

### Filegroups
Filegroups are used in order to distribute the partitions in a partition scheme  to multiple physical disks or RAID arrays. Filegroups can also be used to separate row data from indices. Such a strategy can improve the performance if the data is distributed to different physical drives with their own disk controllers. It allows the database server to read row and index data independently from each other in parallel because multiple disk heads are reading the pages.

### Data Compression
While data compression consumes more CPU power, it uses less I/O to store and retrieve the same amount of data.

## Setting Up the Data Warehouse
### Stage Area
The goal of the stage area is to stage incoming data in order to reduce the workload on the operational systems and shorten the access time to them. The stage area is defined as a temporary storage of the incoming data. It can be a relational database system or a NoSQL storage. Therefore, the goal of the stage area is to collect the incoming data as fast as possible.

### Data Vault
The purpose of the Data Vault layer is to permanently store the enterprise data with all its history. The goal of the Data Vault layer (the data warehouse layer) is to keep a nonvolatile copy of every change of data in multiple source systems, integrated using the business key.

The Data Vault layer also gathers and retains the metadata, metrics data and information about errors. A good practice is to separate each vault using database schemas.

### Information Marts
Both the Business Vault and information marts have much more tolerance to hardware faults than the Raw Data Vault. That doesn’t mean that we welcome hardware faults in the information marts, as it would be a lot of work to replace the disks and rebuild the databases used by the information marts. However, our statement is that it is possible to recreate them without any data loss. Our recommendation is to use individual databases for information marts.

### Meta, Metrics, Error Marts
The Meta Mart, Metrics Mart, and Error Mart are special instances of information marts which are primarily used by IT to analyze internals of the data warehouse.

- Metrics mart: Because it can be rebuilt and reloaded very easily, it can be stored on less reliable RAID configurations, such as RAID-0.
- Meta mart:  Because it is the central place of storage, it has higher reliability requirements than other information marts. Instead, the requirements are comparable to the raw Data Vault layer, where a RAID-5 or RAID-1 level is typically used.
- Error mart: It is the central location of all error information in the data warehouse. Therefore, it should be kept on RAID-5 or RAID-1.
