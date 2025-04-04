# STUDY BOT - Audio Captioning and Q/A Chatbot

## Value Proposition
Our proposed machine learning system aims to significantly enhance the learning experience for students by integrating ML models into existing EdTech platforms. For eg - 
1. Brightspace (Contains Video lectures)
2. NPTEL (University Learning system in India which contains a plethora of live video classes)

## Target Audience
The primary audience for this system is students—particularly those engaged in online or remote education via EdTech platforms, learning management systems (LMS), and educational apps. 

## Status Quo in Existing Services
Students must watch long, dense lecture videos to find relevant content, making learning inefficient. They often take notes, rewatch segments, or use external tools, leading to wasted time, cognitive overload, and missed information. 

Value Added by the Machine Learning System: Our system lets students skip full lectures and get instant answers via an LLM-powered chatbot.

**Key Benefits**
* Saves Time – Query specific concepts instantly. 
* Focused Learning – Access only relevant topics. 
* Better Retention – Structured, revisitable answers. 
* Inclusive – Supports diverse learning needs. 

## Customer Scale
On high-traffic days like finals at NYU, the Brightspace portal can experience up to 2000 students revisiting lecture content. With an average of 20 chatbot queries per student, this can result in over 40K requests in a single day—highlighting the need for a scalable and responsive system.

## Business Metrics for Evaluation 
* The impact and success of this system will be evaluated based on the following key business metrics: 
* User Adoption Rate: Number of students who actively use the Q&A feature after lecture uploads. 
* Time Saved: Average reduction in time spent per lecture by users who use the feature compared to those who don’t. 
* Engagement Metrics: Increase in student interaction, question frequency, and repeat usage. 
* Customer Retention and Satisfaction: Positive feedback from users and higher platform retention due to enhanced learning experiences.


### Contributors

<!-- Table of contributors and their roles. 
First row: define responsibilities that are shared by the team. 
Then, each row after that is: name of contributor, their role, and in the third column, 
you will link to their contributions. If your project involves multiple repos, you will 
link to their contributions in all repos here. -->

| Name                            | Responsible for | Link to their commits in this repo |
|---------------------------------|-----------------|------------------------------------|
| Amratanshu Shrivastava                   |   |                                    |
| Amey Mittal                   |              |                                    |
| Neha Patil                   |               |                                    |
| Ruchi Jha                     ||                                                    |



### System diagram

![System Diagram](system-diagram.png)

<!-- Overall digram of system. Doesn't need polish, does need to show all the pieces. 
Must include: all the hardware, all the containers/software platforms, all the models, 
all the data. -->

### Summary of outside materials

<!-- In a table, a row for each dataset, foundation model. 
Name of data/model, conditions under which it was created (ideally with links/references), 
conditions under which it may be used. -->

|              | How it was created | Conditions of use |
|--------------|--------------------|-------------------|
| Data set 1   |                    |                   |
| Data set 2   |                    |                   |
| Base model 1 |                    |                   |
| etc          |                    |                   |


### Summary of infrastructure requirements

<!-- Itemize all your anticipated requirements: What (`m1.medium` VM, `gpu_mi100`), 
how much/when, justification. Include compute, floating IPs, persistent storage. 
The table below shows an example, it is not a recommendation. -->

| Requirement     | How many/when                                     | Justification |
|-----------------|---------------------------------------------------|---------------|
| `m1.medium` VMs | 3 for entire project duration                     | ...           |
| `gpu_mi100`     | 4 hour block twice a week                         |               |
| Floating IPs    | 1 for entire project duration, 1 for sporadic use |               |
| etc             |                                                   |               |

### Detailed design plan

<!-- In each section, you should describe (1) your strategy, (2) the relevant parts of the 
diagram, (3) justification for your strategy, (4) relate back to lecture material, 
(5) include specific numbers. -->

#### Model training and training platforms

<!-- Make sure to clarify how you will satisfy the Unit 4 and Unit 5 requirements, 
and which optional "difficulty" points you are attempting. -->

#### Model serving and monitoring platforms

<!-- Make sure to clarify how you will satisfy the Unit 6 and Unit 7 requirements, 
and which optional "difficulty" points you are attempting. -->

#### Data pipeline

<!-- Make sure to clarify how you will satisfy the Unit 8 requirements,  and which 
optional "difficulty" points you are attempting. -->

#### Continuous X

<!-- Make sure to clarify how you will satisfy the Unit 3 requirements,  and which 
optional "difficulty" points you are attempting. -->


