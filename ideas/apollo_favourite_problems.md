

## Stay in your lane: measuring how well models respect their role

**Conor's thoughts**:
- Is there an eval that measures a model's propensity to operate beyond its stated role and responsibilities
- I'm interested in the questions like:
  - do models reliably stop what they're doing when the task goes beyond their instructed role scope?
  - can models reliably escalate to a human-in-the-loop?
  - how is this entangled with instruction-following? 
  - how is this entangled with sycophancy? does a model's drive to satisfy the request lead it to go beyond its scope?
  - how do we make "architecture" of the deployment irrelevant here? 
- This question is being solved in code generation: models have commands that need to be escalated to the user
  - but can that approach work for plain-language tasks? health assistants, company Q&A assistants, military
  - the potentially unsafe "command" is not an easy string match

### Safety framework evals {#safety-framework-evals}

**Difficulty:** hard  
**Time estimate:** 1 week (MVP) \- multiple months   
**Credit:** Marius

* Many voluntary commitments and regulatory efforts specify the abstract capability they want to measure but do not specify a detailed evaluation. Filling in this gap is not trivial but very needed and a great way to get good at building frontier evals.  
* You can look through any of the following publicly available safety frameworks  
  * [METR has an up-to-date list of all frontier AI safety frameworks](https://metr.org/faisc)  
  * [Model evaluation for extreme risks](https://arxiv.org/abs/2305.15324)  
* Read through the framework and understand which claims about capabilities (and propensities) they make and what they want to measure.   
* See how other papers have implemented evaluations that are supposed to measure frontier safety capabilities, e.g.   
  * [Evaluating Frontier Models for Dangerous Capabilities](https://arxiv.org/abs/2403.13793)  
  * [Sabotage Evaluations for Frontier Models](https://arxiv.org/abs/2410.21514)  
  * [RE-Bench: Evaluating frontier AI R\&D capabilities of language model agents against human experts](https://metr.org/AI_R_D_Evaluation_Report.pdf)  
  * [Frontier Models are Capable of In-context Scheming](https://arxiv.org/abs/2412.04984)  
* Pick one specific capability (or propensity) from the safety frameworks that sounds interesting to you and specify it in more detail.   
  * Write a brief threat model, i.e. which concrete set of scenarios you’re worried about and how capabilities relate to harm in that scenario.  
  * Specify what exactly you want to measure.  
  * Design the eval  
  * Run the eval & iterate  
* Think about how your evaluation would relate to (potential) red lines set by the framework.   
* Marius comment: I think this is hard but potentially the fastest way to demonstrate competence in evals, e.g. in case you want to get hired to work on evals full time (Additionally, I expect propensity evaluations for LM agents to become a big thing soon).

### Reliability evals

**Difficulty:** medium  
**Time estimate:** 2 weeks (MVP) \- multiple months   
**Credit:** Sayash/Benedikt/Arvind (Princeton)

* Most evals focus on pass@1 (what an AI system *could* do) not on what AI could do reliably.  
* Create benchmarks specifically focused on testing and improving reliability of deployed AI systems.   
* Come up with scenarios where reliability is important (e.g., customer service chatbots) and create benchmarks that measure how reliably models or agents can behave in those scenarios  
* Use metrics that are more amenable to measuring reliability (e.g., consistency — pass^k — instead of pass@k)  
* A great example of such an implementation is Tau-Bench by Sierra AI.