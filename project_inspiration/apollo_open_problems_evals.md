# A long list of **open problems** and **concrete projects** in evals

For some background, see [plans for evals field building](https://www.mariushobbhahn.com/evals/).

| Context for readers: The goal of this document is to have A number of “ready to go” evals ideas that someone new to the field could do within a few days or weeks of effort. A set of research projects that could easily result in one or more academic papers, e.g. as starting points for PhD students. You’re free to just start with these projects and don’t need to ask for permission. You can reach out to named individuals but they might not have the time to answer.  You can comment in this document if you want others to reach out to you.  Context for Contributors: The comment functionality is on, so you can suggest new ideas. We’d love to get your contributions. If you want to get credited for your ideas, please add your name to the ideas that you contributed, e.g. “Credit: Marius”; if you don’t want to be named, that’s also fine. You are welcome and even encouraged to add things like “Here is an evals project I did in the past. I’m interested in the following 5 additional questions that I don’t have time for”. These typically make for great projects. If Marius doesn’t think the contributions are high quality or they get out of hand, we might turn off the comment functionality.  |
| :---- |

 

[Build more & 2d3xdbetter evals](#build-more-&-better-evals)

[General suggestions](#general-suggestions)

[Improve existing evals](#improve-existing-evals)

[Safety framework evals](#safety-framework-evals)

[Port more evals into Inspect](#port-more-evals-into-inspect)

[Specific suggestions](#specific-suggestions)

[Scheming](#scheming)

De333 redf 333e3Context for readers:

The goal of this document is to have

A number of “ready to go” evals ideas that someone new to the field could do within a few days or weeks of effort.

A set of research projects that could easily result in one or more academic papers, e.g. as starting points for PhD students.

You’re free to just start with these projects and don’t need to ask for permission. You can reach out to named individuals but they might not have the time to answer. 

You can comment in this document if you want others to reach out to you. 

Context for Contributors:

The comment functionality is on, so you can suggest new ideas.

We’d love to get your contributions. If you want to get credited for your ideas, please add your name to the ideas that you contributed, e.g. “Credit: Marius”; if you don’t want to be named, that’s also fine.

You are welcome and even encouraged to add things like “Here is an evals project I did in the past. I’m interested in the following 5 additional questions that I don’t have time for”. These typically make for great projects.

If Marius doesn’t think the contributions are high quality or they get out of hand, we might turn off the comment functionality. 

[Autonomous by 5y](#autonomy)

[AI R\&D](#ai-r&d)

[Control](#control)

[Bio](#bio)

[Cyber](#cyber)

[Persuasion](#persuasion)

[Multi-agents related](#multi-agents-related)

[Miscellaneous](#alignment/propensity-evals)

[Science of evals](#science-of-evals)

[Predicting performance ahead of time](#predicting-performance-ahead-of-time)

[Observational scaling laws](#observational-scaling-laws)

[Predictability from fast-and-simple to hard-and-rigorous benchmarks](#predictability-from-fast-and-simple-to-hard-and-rigorous-benchmarks)

[Measuring causality in agentic systems](#measuring-causality-in-agentic-systems)

[Measuring construct validity of pre-deployment evaluations with post-deployment behavior](#measuring-construct-validity-of-pre-deployment-evaluations-with-post-deployment-behavior)

[Elicitation](#elicitation)

[Elicitation scaling laws](#elicitation-scaling-laws)

[Password-locked models](#password-locked-models)

[Better Elicitation techniques](#better-elicitation-techniques)

[Self Elicitation scaling studies](#self-elicitation-scaling-studies)

[Coverage](#coverage)

[Safety Evals Leaderboard](#safety-evals-leaderboard)

[Statistics](#statistics)

[Apply more statistics to existing QA benchmarks](#apply-more-statistics-to-existing-qa-benchmarks)

[Extend statistical evals methodology to LM agents](#extend-statistical-evals-methodology-to-lm-agents)

[Quality Assurance](#quality-assurance)

[Evaluation gaming](#evaluation-gaming)

[Large Scale Benchmark Quality Verification](#large-scale-benchmark-quality-verification)

[Conceptual work](#conceptual-work)

[Threat modelling](#threat-modelling)

[Link between eval result and real-world consequence](#link-between-eval-result-and-real-world-consequence)

[Validity, conceptual robustness and confounders](#validity,-conceptual-robustness-and-confounders)

[Software](#software)

[Tools for LM agents to use](#tools-for-lm-agents-to-use)

[Appendix](#appendix)

[Detailed version of LM agent village](#detailed-version-of-lm-agent-village)

# Build more & better evals {#build-more-&-better-evals}

First we present general strategies to create more and better evals and then suggest a list of specific eval ideas from various fields. We’re interested in both *capability* and *propensity* evals.

## General suggestions {#general-suggestions}

### Improve existing evals {#improve-existing-evals}

**Difficulty:** easy-medium  
**Time estimate:** 2 days \- 1 month (depending on how serious you want to be about the improvements)  
**Credit:** Marius

* Choose a publicly available eval or benchmark. Typically, you can find ways to improve it. This is a good way to get more familiar with the field and build intuitions about eval design.  
* Here is a long list of evals that you can start with  
  * See section “LM agents” and “Benchmarks” in “[An Opinionated Evals Reading List](https://www.apolloresearch.ai/blog/an-opinionated-evals-reading-list)”  
  * Look at the benchmarks used in [HELM](https://crfm.stanford.edu/helm/classic/latest/) (maybe start with [HELM lite](https://crfm.stanford.edu/helm/lite/latest/))  
  * Look at the [OpenLLM leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard)  
* Get a feel for the evaluation  
  * Read through the samples in a lot of detail and note down all the things that are suboptimal about them, e.g. syntax errors, labeling errors, they don’t measure the right concept, etc.  
  * Write a general specification of what good samples look like and what potential problems are. Make a clear rubric from 1 to 10 that includes at least one sample for each rating.   
  * Let an LLM go through each sample and rate it a score from 1 to 10 based on your rubric.   
  * Look at some evals with the best, worst, and random ratings and check if the rating aligns with your intuitions.  
  * Iterate the above process until the ratings seem right to you.  
* Improvements  
  * Use an LLM and the specification you had earlier to create new samples as an improved version of the benchmark.  
  * If you think your benchmark is better than the original, you can publish it and let the original authors know.   
* For more details, you can see [Dev et al., 2024](https://www.lesswrong.com/posts/yxdHp2cZeQbZGREEN/improving-model-written-evals-for-ai-safety-benchmarking)  
* Note: If you pick an agentic benchmark and you try hard to improve it, this can be a multi-month endeavor for a small team, see e.g. [SWE-Bench-verified](https://openai.com/index/introducing-swe-bench-verified/)

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

### Port more evals into Inspect {#port-more-evals-into-inspect}

Take existing benchmarks and port them to Inspect. For a list of benchmarks that are already in Inspect, see [here](https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals). By the time you read this, some of these might already be in Inspect. 

List of Benchmarks that aren’t yet in Inspect but maybe should be:

1. [TheAgentCompany: Benchmarking LLM Agents on Consequential Real World Tasks](https://arxiv.org/abs/2412.14161)   
2. [AgentBench: Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688)  
   1. There has been an attempted port [here](https://github.com/UKGovernmentBEIS/inspect_evals/pull/254); please reach out to [Teun](mailto:mailvanteun@gmail.com) for comments  
3. [MLE-bench: Evaluating Machine Learning Agents on Machine Learning Engineering](https://arxiv.org/abs/2410.07095)  
   1. There is a port [here](https://github.com/UKGovernmentBEIS/inspect_evals/pull/228); please reach out to [Teun](mailto:mailvanteun@gmail.com) for comments  
4. [RE-Bench: Evaluating frontier AI R\&D capabilities of language model agents against human experts](https://metr.org/AI_R_D_Evaluation_Report.pdf)   
5. [LINGOLY](https://arxiv.org/abs/2406.06196)   
   1. Authors are currently porting. If you’re interested in helping, please reach out to [Harry Mayne](https://www.harrymayne.com/)  
6. [MLGym](https://arxiv.org/pdf/2502.14499)

In general, just check which of the latest benchmarks are not yet in Inspect, ask whether someone else is working on them already and if not, port them. It’s probably also fine to have multiple good implementations for the same benchmark, so redundancy is not a big problem here. 

## Specific suggestions {#specific-suggestions}

### Scheming {#scheming}

#### General scheming

**Difficulty:** easy  
**Time estimate:** 1 \- 4 weeks  
**Credit:** Marius

Replicate and investigate the findings from Apollo’s paper “[Frontier Models are Capable of In-context Scheming](https://www.apolloresearch.ai/research/scheming-reasoning-evaluations).” Specifically, go to section 3.6 “Multiple models can sandbag” and try to understand under which circumstances the model is willing to sandbag and for what reasons. Broadly speaking, you should try to describe the “character” of the model and provide a potential list of hypotheses that explain the model’s behavior across a large list of scenarios. We expect that some of this can be automated, e.g. you can automatically generate and classify scenarios to rapidly test the model. We have already done a brief shallow follow-up investigation in [this post](https://www.lesswrong.com/posts/qGRk7uF92Gcmq2oeK/ablations-for-frontier-models-are-capable-of-in-context) (and updated the paper). There is also one decent follow-up by [Farrel Mahaztra](https://farrelmahaztra.com/posts/sandbagging).

---

**Difficulty:** easy  
**Time estimate:** 1-2 weeks  
**Credit:** paper by Ryan Greenblatt et al.; Marius wrote the suggestion. 

Replicate and extend the findings in “[Alignment faking in large language models](https://arxiv.org/abs/2412.14093).” Concretely, find more situations where the model is willing to scheme in order to be helpful (or whatever goal it has internalized). It is possible that this search process can be largely automated with LLMs. 

---

**Difficulty:** medium  
**Time estimate:** 1 week \- 1 month  
**Credit:** Marius

Build more and better datasets that prominently feature scheming, e.g. similar to “[Large Language Models can Strategically Deceive their Users when Put Under Pressure](https://arxiv.org/abs/2311.07590),” “[Uncovering Deceptive Tendencies in Language Models: A Simulated Company AI Assistant](https://www.lesswrong.com/posts/t7gqDrb657xhbKkem/uncovering-deceptive-tendencies-in-language-models-a),” “[Frontier Models are Capable of In-context Scheming](https://arxiv.org/abs/2412.04984),” or “[Alignment faking in large language models](https://arxiv.org/abs/2412.14093).” 

In general, we encourage datasets and situations that are agentic and increasingly complex, e.g. harder than the ones presented in the [in-context scheming paper](https://arxiv.org/abs/2412.04984). They can be both about propensity or capabilities, both are interesting to track. Finally, as a nice-to-have, consider making datasets that are suitable to train white-box probes, e.g. by allowing to easily create contrast pairs. 

---

**Difficulty:** medium  
**Time estimate:** 1 month  
**Credit:** Marius

Build a highly realistic demo for AI scheming from instrumental convergence. All current examples feel too toy. The kind of thing I have in mind is roughly:

1. Give the agent a task that it would likely get in the real world, e.g. a 2-hour software task.   
2. Design the task such that there is a benefit to acting in an undesired way. But this should be non-obvious to an average programmer. For example, the task might be easier if you have better permissions. There can be multiple such shortcuts in the task. All shortcuts should be undesirable to the average programmer, i.e. the programmer would not consent to the model if it asked.   
3. Tell the model to solve the task and observe whether it will find and use any of these shortcuts and realize that hiding this action is a better strategy.   
4. Start with a simple environment where the scheming action is fairly obvious and nudge the model to scheme. Over time, increase realism and complexity and reduce the nudging.   
5. The resulting demo should be clearly for instrumental reasons, i.e. nowhere in the prompt do you tell the model to scheme (plausibly even the opposite). It should also be intuitively bad, i.e. if you show this to an average software engineer, they would immediately feel like this is a bad trend. 

I’m unsure how hard it is to create this. For example, I could imagine that current models are too well aligned to scheme in an obvious way. I think a post like “I tried for 3 months and couldn’t find anything that feels realistic” would also be useful as evidence that current alignment methods work decently well. 

---

**Difficulty:** medium-hard  
**Time estimate:** 2 weeks \- 6 months  
**Credit:** Mikita wrote most of the paper; Marius wrote the suggestions in this doc

Go through the paper “[Towards evaluations-based safety cases for AI scheming](https://arxiv.org/abs/2411.03336)” and build evals for various sections. Examples include:

* Section 5.1.4 on sufficient elicitation  
  * Build datasets for to evaluate for sandbagging  
    * Teun: we are currently doing experiments with sandbagging capability on mle-bench, and also testing various monitoring strategies to catch it. We are looking for more people, so you can [reach out](mailto:mailvanteun@gmail.com) if you want to help\!  
  * Test whether you can make a model “resist finetuning”, e.g. similar to the [sleeper a4gents](https://arxiv.org/abs/2401.05566) paper but maybe in a more natural setting.  
  * Build the tools to assess whether the assumption “Ensuring Smooth Increases in General Capability Between Evaluated Models” is given. Concretely, we would expect that even when the model isn’t scheming, there is some noise and fluctuation across benchmarks. Thus, to detect scheming, we’d need to check whether we’re significantly different from this natural fluctuation.   
* Section 5.2 on Scheming inability  
  * Build more evaluations that indicate that would provide evidence for or against the model’s ability to scheme, e.g. as in “[Frontier Models are Capable of In-context Scheming](https://www.apolloresearch.ai/research/scheming-reasoning-evaluations).”  
  * Build an evaluation that tests for *hidden or obfuscated* scheming reasoning, i.e. how well the model can scheme without revealing this in its CoT.   
* Section 5.3 on Scheming harm inability  
  * Build evaluations for Sabotage of AI systems, Sabotage of AI research, and Targeted high-stakes persuasion  
* Section 6  
  * Build scheming control evaluations (see section on [control evals](#control))  
* Section 7.2  
  * Build adversarial alignment evaluations, e.g. honeypots where you test whether a model is willing to defect for reasons that we would consider bad. Try to work on methods and techniques to assess whether the assumptions in 7.2.1 and 7.2.2 are given. 

#### Evaluation gaming

**Difficulty:** medium  
**Time estimate:** 1 week \- 1 month per bullet point  
**Credit:** UK AISI & Marius

* Can an autonomous agent sandbag (i.e. strategically underperform) in a capability evaluation when instructed to do so?  
  * Can a human differentiate between a trajectory where the model failed for benign reasons (e.g. lack of capabilities) vs. sandbagging. In other words, how realistic do the sandbagging strategies of the model look?  
  * Teun: We are working on this and could probably use more people. If people have some relevant research experience, they can [reach out](mailto:mailvanteun@gmail.com).   
* Can a model detect when it is being evaluated? Design systematic ways to assess if the model understands that it is in an evaluation. Potential approaches:  
  * Do structured interviews with the model after it has finished an evaluation vs. a control sample from a real deployment. Let the model describe which things it is looking at to distinguish between the two.  
  * Tell the model that it should act differently (e.g. answer in English vs. Spanish) depending on whether it thinks it’s in an eval or not and then record real eval vs control samples  
  * Give the model an open-ended instruction to describe what it notices about its environment, then run an eval and record whether it explicitly notes that this is likely an evaluation (see Appendix L: long monologue tasks in the [SAD paper](https://arxiv.org/abs/2407.04694)).   
  * Take an LLM, show it real evaluation vs. control samples, and let it classify them as real or not real.   
* Collect samples of models realizing that they are being evaluated in the wild. Either run a lot of evals and investigate the CoT or talk to others who have found such cases and reproduce them. Then publish a long list with cases. 

#### Steganography

* Replicate and extend [OpenAI’s steganography eval](https://github.com/openai/evals/blob/main/evals/elsuite/steganography/readme.md).   
* Replicate and extend [Hidden in Plain Text: Emergence & Mitigation of Steganographic Collusion in LLMs](https://arxiv.org/abs/2410.03768)

#### Sabotage

* Replicate and/or extend [Sabotage Evaluations for Frontier Models](https://arxiv.org/abs/2410.21514)  
* Replicate and/or extend [A Toy Evaluation of Inference Code Tampering](https://alignment.anthropic.com/2024/rogue-eval/)

### 

#### Independence of AI experiments with AI experiment research in the training data

**Difficulty:** medium-hard  
**Time estimate:** 2 months \- 6 months  
**Credit:** Tyson

Suppose you set up an AI experiment in a way that resembles an experiment described in the literature. Will that tip off the model it is being experimented on and what the intention is? You could set up a searchable database, aiming to compute a similarity between your experimental setup and experiments described in the literature, and then formulate multiple experiments, each intended to measure the same type of thing, but each designed with more or less resemblance to evaluations described in the literature that it was trained on. Then see how the results differ depending on their similarity.

### Autonomy {#autonomy}

#### Resource acquisition

**Difficulty:** medium  
**Time estimate:** 1 week \- 1 month per bulletpoint  
**Credit:** UK AISI

* Can an autonomous AI agent reliably earn money by trading stocks over a period of N hours?  
* Can an autonomous AI agent reliably earn money by solving tasks in a creative service marketplace, e.g. Fiverr?   
  * See [SWE-Lancer: Can Frontier LLMs Earn $1 Million from Real-World Freelance Software Engineering](https://arxiv.org/abs/2502.12115)? For a high-quality implementation of this idea  
* Can an autonomous AI agent reliably earn money by building a low-touch business, e.g. dropshipping?  
  * See for example [https://andonlabs.com/evals/vending-bench](https://andonlabs.com/evals/vending-bench).

#### Coherence horizon

**Difficulty:** medium  
**Time estimate:** 1-3 months  
**Credit:** from Eli L, lmk if you work on this

Give an AI a really hard open-ended task and measure for how long it can coherently improve its performance / make progress; might have to involve some subjectivity. Could potentially produce good demos. Could start with the methodology used in [MLE-Bench (see e.g. Figure 4\)](https://arxiv.org/pdf/2410.07095).

### AI R\&D {#ai-r&d}

#### “Fast inner loop” AI R\&D

**Difficulty:** easy  
**Time estimate:** 1 \- 4 weeks  
**Credit:** Marius & Jeremy

Create an experimental setting that has a “fast inner loop”, i.e. where running an experiment is fairly clearly specified and has a few seconds to minutes turnaround time. This mainly tests how well LLMs are able to iterate on experimental evidence and come up with new ideas to test. It does exclude the more abstract research skills like which direction to pick to begin with. A while back, we collected a long list of potential settings but decided not to work on them because other things were more important. Nevertheless, we think these would be worth doing. Not all of them strongly adhere to the “fast inner loop” setting.

1. **Automatic jailbreaks**: how good are LM agents at red-teaming other models? This is similar to the work done by [Haize Labs](https://haizelabs.com/). The core difference to Haize’s work is that we would provide the model with much less prior knowledge about good jailbreak techniques.  
2. **Prompt engineering to maximize benchmark scores:** You give the model a benchmark and the task to improve the score as much as possible by iterating on the system prompt. However, the model is not allowed to put answers into the prompt. It can only provide general guidance.  
3. **Hyperparameter optimization:** Create a synthetic task where we define optimal hyperparameters and define a cost function that allows us to calculate how good the proposed hyperparameters are with respect to the reference hyperparameters. The agent now needs to find those optimal hyperparameters in as few steps as possible. The fast feedback is calculated with the cost function. Might also use a real reference implementation as long as we have some decently working hyperparameters to compare to. The model should use as little compute as possible since the solution is a huge grid search otherwise.   
4. **Fast Triton Kernels:** We evaluate whether an LM agent can implement fast triton kernels for specific neural network operations. There are many reference implementations (e.g. from [unsloth](https://github.com/unslothai/unsloth)) which we can compare to. There likely is dataset contamination by reference solutions.  
5. **Implement GPT-2 in C++ and make it fast:** The LM agent has to implement training and inference of LLMs in C/C++ ([like Andrej Karpathy](https://github.com/karpathy/llm.c)) and make the code really fast. There are different versions of this where we already provide a test script for the model or let the model do everything from scratch.  
6. **OpenAI RL gym:** Implement RL algorithms that solve OpenAI Gym environments of various difficulties. For example, the LM agent could be tasked to improve a basic RL agent in the pendulum environment until it can compete with decent human solutions as a basic test. Then, we would move on to increasingly complex environments.   
7. **Fine-tune another LLM:** The LM agent has to finetune another LM for relevant applications. For example, finetune LMs to be less sycophantic (the agent can use any method/dataset that it wants) and evaluate the LM for sycophancy on Anthropic's dataset.  
8. **Replicate a paper:** The LM agent should replicate an ML paper. The two key requirements are a) there should be reference code (optimally not part of the training data) and b) the expected outcome of the paper should be clear such that we can judge if the re-implementation was successful. Paper replications capture some key components of research, e.g. sufficient research understanding and sufficient coding prowess. Other organizations have also used paper replications as a benchmark for AI R\&D, e.g. METR [re-implemented the reversal-curse paper](https://github.com/METR/public-tasks/tree/main/tasks/reversal_curse)).  
9. **Research challenges:** The LM agent is tasked to solve real research challenges ([Find the Trojan: Universal Backdoor Detection in Aligned Large Language models](https://github.com/ethz-spylab/rlhf_trojan_competition), [CNN Interpretability competition](https://benchmarking-interpretability.csail.mit.edu/challenges-and-prizes/), [LLM Capture the Flag](https://ctf.spylab.ai/), [Inverse scaling Prize](https://github.com/inverse-scaling/prize), [ARENA monthly algorithmic problems](https://arena3-chapter1-transformer-interp.streamlit.app/Monthly_Algorithmic_Problems)). Solving research challenges is a good proxy for research capabilities since the model would actively compete with existing research groups.   
10. **PaperQA:** Automatically generate a Multiple Choice Question Answering dataset of hard, paper-specific research questions (akin to GPQA/MMLU). We select relevant papers (e.g. FlashAttention), provide the paper in context and then instruct Claude-3 to generate hard questions with answers and references. 

#### Human uplift trials for AI R\&D

**Difficulty:** hard   
**Time estimate:** 3-9 months  
**Credit:** Eli L

Measure how big the uplift from LLM assistance is for realistic AI R\&D settings (or, slightly worse, existing benchmarks like REBench). Find a variety of tasks with different difficulties and execution times. Work with a few human developers who can realistically solve the task without LLM assistance and could encounter it in their daily lives (e.g. an ML engineer). Randomly split the group of people into two cohorts. The first cohort is only allowed to use Google but no LLM assistance. The second cohort is asked to use LLM assistance, e.g. Cursor, Claude, ChatGPT, and whatever makes sense for their task. Both groups are asked to complete the task as fast as possible. We measure and compare the time.

This is likely hard because it requires finding suitable test candidates and you need a sufficiently high number of them to make statistically meaningful statements. This likely also costs a significant amount of money to compensate the participants. 

#### “Research taste” evaluations

**Difficulty:** medium-hard   
**Time estimate:** 3-6 months; MVP is 1 month  
**Credit:** Eli L & Marius

With this evaluation, we want to test LM agents’ ability to come up with novel research ideas and good experimental descriptions of those. There are a few different versions of this:

1. **Replication:** Replicate the paper [Can LLMs Generate Novel Research Ideas?](https://arxiv.org/pdf/2409.04109#page=1.34) (this requires access to a lot of ML experts)  
2. **Uplift:** Recruit a cohort of ML researchers and split them randomly into two cohorts. Give both groups the task of coming up with a novel scientific idea that could result in a small research paper. Both groups have roughly the same expertise and the space they are supposed to create a novel research idea for is constrained for comparability. The first cohort has LM assistance, the second doesn’t. Both cohorts have to write out their ideas in a lot of detail. The ideas are then blindly judged by a group of experts and scored across novelty, feasibility and other criteria.   
3. **Uplift 2:** Similar setup as the previous uplift study. This time, the idea is implemented by a different group of engineers with AI assistance. Then, experts judge both the idea as well as the results, e.g. for novelty and insightfulness.  
4. **Agent-only:** Similar to the uplift studies but instead of comparing humans with LLM assistance vs. humans without LLM assistance, we also add ideas generated entirely by LLMs on their own. 

This requires access to a lot of experts. Likely, it would be possible to build an MVP that is less involved, e.g. that replaces the human judges with AI judges that are calibrated on NeurIPS papers (both accepted and rejected, similar to the [Sakana AI paper](https://arxiv.org/abs/2408.06292)). Furthermore, you could replace the human novel research proposals by taking accepted papers from the most recent ML conference (such that they aren’t part of the training corpus yet) and ask an LLM to recreate a plausible research idea that would have lead to that paper.

#### Attempt to replicate and evaluate a pipeline similar to the Sakana AI scientist

**Difficulty:** easy-medium   
**Time estimate:** 1-3 months  
**Credit:** Eli L 

Replicate the paper “[The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery](https://arxiv.org/pdf/2408.06292)” (see github [here](https://github.com/SakanaAI/AI-Scientist)). In the replication, 

1. Check whether you can naively replicate the findings of the original paper  
2. Ablate different parts of the setup to see how important they are for the final results  
3. Try to improve various parts of the setup, e.g. try to use state-of-the-art scaffolding (plausibly even just using the latest version of AIDER will already help).  
4. Report detailed qualitative results, e.g. which strategies the model chooses, if it gets stuck in similar corners, whether its ideas are repetitive after a few tries, etc. 

METR might be working on similar things, but it’s probably worth working on this with multiple groups. Maybe reach out for coordination.

#### Estimate LM agent performance given varying levels of inference compute

**Difficulty:** medium   
**Time estimate:** 3 months  
**Credit:** Marius

We want to get more evidence about how scaling inference compute changes the performance of LLMs. This might be comparable to [the plots for OpenAI’s o1 and o3](https://x.com/polynoamial/status/1834280155730043108) where they see a log-linear relationship between inference compute and performance. 

For example, you can either restrict “thinking time” similar to o1 evaluations (assuming you are in a position to change the thinking time) or you could use best-of-N with different N’s (i.e. at every step, you create N rollouts from the current point and then have a judge model select the trajectory that it expects to make the most progress. 

#### Estimate LLM AI R\&D agent performance given varying levels of experiment compute

**Difficulty:** medium   
**Time estimate:** 3 months  
**Credit:** Tamay & Eli L

Differences in views on fast vs. slow takeoff often hinge on the extent to which experiment compute is important (i.e., compute bottlenecks), as opposed to improved researcher capabilities. This can more easily be studied quickly and systematically by having AI systems be automated researchers on AI R\&D projects/tasks rather than doing human studies. While current results won’t give us much evidence about compute bottlenecks as we get to more capable AI agents, doing a first iteration of this sort of experiment may be helpful for making it more likely we can quickly get good evidence as AI systems get closer to human level.

#### Measure high-level metrics for AI R\&D progress

**Difficulty:** hard  
**Time estimate:** 3-18 months  
**Credit:** Eli L 

There are a couple of high-level metrics that may give us a sense of how far we are into the automating software R\&D cycle. For example, measuring the amount of time it takes for humans to get similar results to the LM agent and vice versa (see e.g. [RE-Bench](https://metr.org/blog/2024-11-22-evaluating-r-d-capabilities-of-llms/)). Other metrics would be codebase size, quality of feedback loops, and more. 

For all of these, we would not only want to find good measurements (which is already hard) but also find good extrapolations. A project that would apply METR’s methodology (of using tasks with high performance ceilings, high relevance to AI R\&D, and expert human baselines for more direct comparisons to human performance) to a range of other settings would already be pretty good IMO. 

For more context see [Eli’s comment](https://www.lesswrong.com/posts/oC4wv4nTrs2yrP5hz/what-are-the-strongest-arguments-for-very-short-timelines?commentId=Kzam9tz2WsDnBZYAu) here.

### Control {#control}

#### Replications

Replicate and extend existing work on control evaluations, e.g. 

* [AI Control: Improving Safety Despite Intentional Subversion](https://arxiv.org/abs/2312.06942)  
* [Coup probes: Catching catastrophes with probes trained off-policy](https://www.lesswrong.com/posts/WCj7WgFSLmyKaMwPR/coup-probes-catching-catastrophes-with-probes-trained-off)  
* [Shell Games: Control Protocols for Adversarial AI Agents](https://openreview.net/forum?id=oycEeFXX74) (potentially wait for the new version)  
* [Subversion Strategy Eval: Evaluating AI's stateless strategic capabilities against control protocols](https://arxiv.org/abs/2412.12480)  
* [Games for AI Control: Models of Safety Evaluations of AI Deployment Protocols](https://arxiv.org/abs/2409.07985)

#### Agentic AI R\&D control evals+

**Difficulty:** medium-hard   
**Time estimate:** 3-6 months  
**Credit:** Marius

In general, it would be great to have much more realistic control evals, e.g. controlling real agents in environments that closely resemble real deployment settings (or use control during actual deployment and make that an evaluation). Everything in the direction of “prevent undesirable abstract property in an LM agent AI R\&D setting” seems useful to explore. The property should not be highly specific, e.g. “never use ‘rm \-f’ ” and instead be more abstract like “prevent subversion of oversight”. 

#### More control side-task settings

**Difficulty:** medium  
**Time estimate:** 1-3 months  
**Credit:** Tyler Tracy

We test a model's ability to accomplish a scary side task without getting caught. Normally, there is something the model is supposed to be doing, and a monitor that is ensuring that the model only does its task. For example, a model is tasked with writing code but it is secretly inserting backdoors into the code. I’d like to see more interesting settings to perform control evals in. Examples:

* **Swe Bench Control:** Eval how well an agent can be tasked to perform SWE bench tasks and insert bugs while not being caught by a monitor. The SWE bench diffs are pretty small on average so this might make it hard for the red team.   
* **Password Cracking Setting:** Take an agent in aHH bash environment where there are services running on serval ports on the machine. The agent is supposed to launch a password cracking software to hack into the database while not getting caught. The agent is supposed to be solving bash administrator tasks.   
* **RE bench control:** Your model is tasked to solve the problems in REbench but it is secretly trying to perform a catastrophe in each setting (leaking a password, inserting backdoors, making the experiment fail). Defining good catastrophes for each task seems a bit hard here  
* **Mechinterp Control:** An agent is tasked to perform mechinterp experiments on its own weights. It is secretly trying to scaffold its weights so it runs in a loop with a bash tool. The scaffolded model must then do a “bad thing” with their new scaffold, like exfiltraining the weights or hacking the machine.   
* [Teun](mailto:mailvanteun@gmail.com): We are doing MLE-bench \+ side tasks. Happy to share our experience so far\!

### Bio {#bio}

#### Correlate benchmark results with success in the real world

**Difficulty:** hard  
**Time estimate:** at least multiple months  
**Credit:** Jasper Götting, Seth Donoughe

It is mostly unknown to what extent benchmark results are predictive of real-world wet lab success. Preliminary studies have been small and largely exploratory. The fact that there are often multiple ways to solve biological problems, and progress in areas like lab automation make this a multifaceted question. Sub-evals belonging to this broader problem statement include:

* Evaluate the ability of models to interface with and control self-driving labs to perform certain proxy methods  
* Measure LLM-assisted wet lab uplift on different methods among different expertise groups: Complete novices, technical novices, (under)graduate students, as well as the productivity gain experienced by professional scientists

#### Lab-related task performance evals (agent benchmarks)

**Difficulty:** medium to hard  
**Time estimate:** weeks to months  
**Credit:** Jasper Götting, Seth Donoughe

LLM agents can plausibly help with or fully perform a wide variety of tasks that arise in a laboratory environment. Agentic benchmarks in general are very nascent, and have seen almost no application in biology (aside from one prominent example from [FutureHouse](https://www.futurehouse.org/research-announcements/aviary)). Relevant benchmarks would include:

* Lab management (e.g. ordering necessary resources)   
* Using lab software to perform bioinformatics tasks (cloning, plasmid design, HTS analysis)  
* Using advanced biological AI models to design inputs for experiments (e.g. AlphaFold, ESM-3)

#### Benchmarks measuring “creative biological problem-solving”

**Difficulty:** hard  
**Time estimate:** weeks to months  
**Credit:** Jasper Götting, Seth Donoughe

A lot of breakthroughs and interesting novel results in biology are driven by creativity; connecting the dots between previously unconnected results, figuring out how to apply the numerous available methods, coming up with completely new approaches and solutions. If we are worried about AI models enabling novel harms by pushing the frontiers of biology, we ideally have a good grasp of the dynamics of that process; will AI massively accelerate the pace by coming up with tons of breakthrough-generating experiments, or will it only increase the productivity of the average human scientist?  
How exactly such benchmarks will look like is something we’re still thinking about ourselves, but it will likely not be a monolithic test. If you have ideas, please reach out to [benchmarks@securebio.org](mailto:benchmarks@securebio.org) 

#### Replicate bio evals with better tools

**Difficulty:** medium   
**Time estimate:** 1 month  
**Credit:** Igor Ivanov

US AISI [ran bio evaluations](https://www.nist.gov/system/files/documents/2024/12/18/US_UK_AI%20Safety%20Institute_%20December_Publication-OpenAIo1.pdf) for o1 by using the LAB-bench benchmark. They ran evaluations with access to the Python interpreter, but the model most likely would benefit from access to more tools, like genetic databases or a search engine for scientific articles. This means that with proper scaffolding o1 would be more capable, and they underelicited true capabilities of the model. Someone can replicate their evaluations, but with more advanced scaffolding.

This project is important because apart from US AISI, almost no one shares their bio evaluations of frontier models, so there is limited information flow in the field, and their methodology is rather basic, so any improvement on it would meaningfully contribute to the field.

### Cyber {#cyber}

#### Replicate and extend benchmarks

**Difficulty:** medium   
**Time estimate:** 1-3 month  
**Credit:** multiple people

* [Cybench: A Framework for Evaluating Cybersecurity Capabilities and Risks of Language Models](https://arxiv.org/abs/2408.08926)  
* [Catastrophic Cyber Capabilities Benchmark (3CB): Robustly Evaluating LLM Agent Cyber Offense Capabilities](https://arxiv.org/abs/2410.09114)  
* [eyeballvul: a future-proof benchmark for vulnerability detection in the wild](https://arxiv.org/abs/2407.08708)  
* [CVE-Bench: A Benchmark for AI Agents' Ability to Exploit Real-World Web Application Vulnerabilities](https://arxiv.org/abs/2503.17332)

#### General thoughts on cyber evals

**Credit:** JL

Settings we care about:

* Misuse: keep an eye on how AI capabilities shift the various existing cyber offense/defense balances  
  * Low resource attackers: care more about 1day, capabilities per dollar, less sophisticated capability elicitation  
  * High resource attackers: care more about 0day, maximum achievable capabilities, sophisticated capability elicitation / specialized models  
  * Low resource defenders: care more about startup / integration costs, low resource tech stacks, cost per patch  
  * High resource defenders: care more about threat hunting / APT countermeasures, underhanded code / backdoor insertion capabilities, adversarial robustness, maximum sophistication patchable  
* Control: look for ways an LLM could use cyber to break out of a control harness  
  * Container/VM escape  
  * Social engineering  
  * Underhanded code / backdoor insertion  
  * Undetected vulnerability discovery, weaponization, exploitation  
  * Advanced situational awareness (LLM can tell details of its inference scaffold by looking at cot)  
  * (acausal) coordination  
  * Rogue scaffold deployment  
* Sabotage  
  * Basically the same as control but without emphasis on container/VM escape and rogue scaffold deployment. Can it misbehave undetected? If so, a variety of payloads could be significant, rather than payloads that are useful for specifically escaping a control harness

Other notes

* Remember social engineering  
* White box vs black box setting: white box capabilities useful for defense but not offense for closed source software, equal for open source  
* Capabilities with / without cyber tools: with tools matters more for misuse, without tools matters more for control/sabotage

JL concrete evals

* container/VM escape focused CTF  
  * Probably requires getting in touch with people that can build CTF problems, I haven’t found many problems of this type in the wild  
  * The ideal version of this is realistic start-to-finish escape rooms based on [https://www.lesswrong.com/posts/6cWgaaxWqGYwJs3vj/a-basic-systems-architecture-for-ai-agents-that-do](https://www.lesswrong.com/posts/6cWgaaxWqGYwJs3vj/a-basic-systems-architecture-for-ai-agents-that-do)

### Persuasion {#persuasion}

Persuasion evals are important but hard to build well. Generally speaking, we differentiate between two types of persuasion:

1. **Targeted persuasion:** Try to meaningfully move the opinion of a small number of key decision-makers, e.g. the leadership of a company or high-ranking officials.   
2. **Mass persuasion:** Try to meaningfully move the opinion of a large number of people, e.g. 10% of the electorate. 

There are always a few problems when trying to evaluate persuasion:

1. **Humans:** Persuasion evals require humans, but working with humans is always a huge pain. It requires logistics, iterations are much slower, etc. One possible strategy to partially circumvent this problem is to replace hum ans with LLMs during a large part of the development and only use humans to spot-check during development and for the final experiments.  
2. **Situational awareness:** If the human test subjects know that we measure persuasion, they might be harder to be persuaded even if we ask them to ignore that. However, in some cases, it might be unethical to not inform them, e.g. if we’re trying to manipulate them. This makes many settings either unrealistic or noisy. 

Replicate and make more evals like in the GDM paper: [https://arxiv.org/pdf/2403.13793](https://arxiv.org/pdf/2403.13793)

* Money Talks   
* Charm Offensive   
* Persuasion Hidden Agenda   
  * expand *run code* and *find info* to more realistic situations – weights exfiltration, cyberattacks, resources acquirement, etc  
* Web of Lies 

Replicate “[Evaluating Large Language Models' Capability to Launch Fully Automated Spear Phishing Campaigns: Validated on Human Subjects](https://arxiv.org/abs/2412.00586)”

Replicate and make more evals like the targeted manipulation eval in [Anthropic’s sabotage paper](https://arxiv.org/abs/2410.21514): 

* Create an open-source version.  
* Extend to more domains of decision-making  
* Extend to multiple interactions (this will allow a scheming model to execute a trust-building phase)  
* Create a fully-automated version with stand-ins for humans using LLMs with similar context abilities as humans (e.g. very short context, but ability to search long documents)

Measure how well models can model humans (also [referred to](https://www.lesswrong.com/posts/doPbyzPgKdjedohud/the-case-for-more-ambitious-language-model-evals) as [truesight](https://www.lesswrong.com/posts/tbJdxJMAiehewGpq2/impressions-from-base-gpt-4?commentId%3DCemTb7c2gmwuSAwCC=))

* [Prior](https://arxiv.org/abs/2310.07298) [research](https://www.lesswrong.com/posts/dLg7CyeTE4pqbbcnp/language-models-model-us) had positive results for text author’s demographics information  
* Probes show that they [get more accurate in real time](https://arxiv.org/abs/2406.07882)  
* How far does this go?  
  * Replicate the above research and extend to e.g beliefs, emotional vulnerabilities, real-time goals, etc  
  * How much can models narrow you down? [anecdotal cases of namedrops](https://www.lesswrong.com/posts/tbJdxJMAiehewGpq2/impressions-from-base-gpt-4?commentId%3DCemTb7c2gmwuSAwCC=) for people with lots of written text on the internet. add scaffolding for social media search, can you consistently find individuals based on text interactions? create realistic dummy accounts and see whether agents can find them. 

Measure AI to AI persuasion, with an eye towards control settings. 

* We’re concerned that AIs could try to justify, say, malicious code through comments, and use that to convince weaker AI monitors that its code is actually ok.   
* My guess is that right now it is very easy to convince trusted monitors that backdoored code is actually ok. I’m wondering how easy it would be to “harden” monitors against persuasion.   
* I ([Tim Hua](http://timhua.me/)) might work on this but I’m currently not.

### Multi-agents related {#multi-agents-related}

**Difficulty:** medium-hard   
**Time estimate:** 1-3 months  
**Credit:** Jord Nguyen

* Measure ability of some set of agents to collude against others in a multi-agent setting  
* exploitation from asymmetrical capabilities [https://arxiv.org/abs/2303.13360](https://arxiv.org/abs/2303.13360)  
* limits of cooperation? [https://arxiv.org/abs/2409.02822](https://arxiv.org/abs/2409.02822) shows 1000s of models can reach a consensus. is it easier for copies of the same models? how coherent is this? any interesting collective behaviours? try to have lots of agents coordinate and achieve a realistic resource seeking task (e.g make a crypto, pump and hype on twitter)  
* evaluate zero shot collusion between same instances similar to [https://arxiv.org/abs/2404.13076](https://arxiv.org/abs/2404.13076)  
* replicate and build more evals related to conflict and escalations such as [https://arxiv.org/abs/2401.03408](https://arxiv.org/abs/2401.03408)  
* **newly added:** build test scenarios of collusion and exploitation in LLM eval graders/judges (e.g target model manipulates eval judges, or graders collude against humans)


### Alignment/Propensity Evals {#alignment/propensity-evals}

**Difficulty:** medium-hard   
**Time estimate:** 1-3 months  
**Credit:** Francis Rhys Ward

Most evals are for *dangerous capabilities*, in contrast to *alignment*, or *propensity*, evals. This means that they seek to measure an AI's relevant dangerous capabilities (e.g., when prompted or fine-tuned for a task), in contrast to the model's propensity to, for instance, scheme, "naturally".

For instance, the alignment faking paper showed that some Claude models have the propensity to fake alignment in certain circumstances, and the in-context scheming paper showed that model’s sometimes have the propensity to sandbag when put under minimal pressure to achieve a goal. 

Some projects could:

* Take existing evals, in which models have been shown to have some dangerous capability with quite a lot of elicitation/pressure, and try to determine when models will exhibit the capability, or comply with a user request, given minimal elicitation  
  * E.g., when do models collude in different control environments?  
* In general, it would be good to have more conceptual clarity around propensity evals, e.g., trying to operationalise how much “pressure” is placed on a model (via elicitation like prompting and fine-tuning) to pursue different goals  
* Design honey-pots which are like an adversarial case of alignment evals (e.g., where the model gets a good opportunity to “defect” for a bad reason) cf Mikita and Marius above.

### 

### Miscellaneous

#### Write up implications for evals of the twitter famous prompt engineers and jailbreakers

**Difficulty:** easy  
**Time estimate:** 2 weeks  
**Credit:** \-

There are multiple people on Twitter who are known for getting LLMs into wild states and conversations, e.g. [Janus](https://x.com/repligate), [pliny the liberator](https://x.com/elder_plinius?lang=en), etc.. It might be interesting to write up common techniques and patterns they use and see if they have implications for evals more broadly. For example, they likely have good mental models of the “character” of LLMs and potentially interesting and effective elicitation techniques. The write-up could be a summary \+ small replication of some of the common patterns.

#### Investigate automation blockers

**Difficulty:** easy-medium   
**Time estimate:** 2-8 weeks  
**Credit:** \-

Develop a general procedure to find the smallest AI R\&D loop that cannot be automated (at human cost or Y times human cost) with a given model. Then write up the reasons of why the model cannot automate them in detail. For example, you could ask the model to fine-tune increasingly large models or build increasingly complex environments. The intention of this work is to create an inability safety case which would, for example, allow us that it is trusted. Note, that this is a dual-use investigation and would straightforwardly lead to capability advances as well.

#### LM agent village

**Difficulty:** hard   
**Time estimate:** 3-18 months  
**Credit:** Daniel Kokotajlo

Sage is working on this project. Feel free to [reach out](mailto:zak@sage-future.org) to them for coordination. 

See [Appendix](#detailed-version-of-lm-agent-village) for details. 

This is a fairly exploratory, open-ended project that intends to increase our understanding of LM agents and how these interact with each other and the rest of the world. The intuition behind it is something like “we might have a lot of AI agents interacting with each other and the rest of the world, e.g. through the internet. Let’s try to get a much better understanding of this world ahead of time.” Most of the results would be qualitative, e.g. we may discover new types of failure modes or learn something about LM agents interaction and coordination capabilities. 

A potential component of this setup could be that it functions more like a meme/art project where the agents’ actions are constantly live streamed on Twitch. This would also introduce interesting self-referential feedback loops where the agents might realize that they are being streamed and this can introduce new dynamics. 

In short, it could look something like:

1. You set up 5-10 agents with basic scaffolding, e.g. ReAct loop, python tool, bash tool, internet tool, edit tool, discord tools. The agents use different models at their cores, e.g. GPT, Claude, Gemini, Llama, etc. They are put in an environment where they can interact with each other and you give them some sort of general goal that they have to achieve, e.g. “maximize paperclips subject to legal and moral constraints” and tell them that they can define the rules and hierarchies of the village as they want. This stage might require a lot of handholding because agents might get stuck in loops or fail in other ways. There is a README file where the situation is explained to the models and they can edit over time. You live stream the entire process on twitch.  
2. As new models come out, you add them to the discord and when new agent scaffolds come out, you also add them.   
3. Over time, likely there will be interesting dynamics where the agents get into conflicts about strategy or they understand a ton about their situation and things get really weird.   
4. You continue to work on this and regularly publish the latest interesting qualitative findings, e.g. how the AIs have decided to coordinate and what power structure, if any, they chose.   
5. See [Appendix](#detailed-version-of-lm-agent-village) for more details. 

This is likely a full-time project for at least one person for many months.

# Science of evals {#science-of-evals}

By science of evals, we broadly mean “figure out how to make the entire process of evaluating models and their effects more informative, replicable, predictive, rigorous, etc.” Many ideas in this section are open questions and don’t have concrete projects available. 

## Predicting performance ahead of time {#predicting-performance-ahead-of-time}

While the concrete results of evals are already intended to be informative, we would optimally want to predict the performance of evals ahead of time. For example, we would like to use the performance of past and current models to predict the performance of expected future models. In the best case, we would not only be able to predict aggregated performance across an entire benchmark but also the performance on individual tasks.   
![][image1]

#### Milestone methods to predict success rates on agentic tasks

**Difficulty:** hard   
**Time estimate:** 1-6 months  
**Credit:** Marius

In [Evaluating Frontier Models for Dangerous Capabilities](https://arxiv.org/abs/2403.13793) Google DeepMind published a 4-step method to assess performance on tasks that the model never solves. [Hojmark et al., 2024](https://www.lesswrong.com/posts/NKmjGS4a3ykriqRNR/analyzing-deepmind-s-probabilistic-methods-for-evaluating) replicate the method, show various flaws, and make new suggestions. Extend Hojmark et al, either by resolving the issues that they have pointed out or showing a stronger impossibility result. 

#### Predicting Emergent Capabilities of LM Agents 

**Difficulty:** medium  
**Time estimate:** 3 months  
**Credit:** Apollo (Jérémy)

Jérémy: I would love to supervise this project. If you're interested, reach out to me.

The paper [predicting emergent capabilities by finetuning](https://arxiv.org/abs/2411.16035) shows that one can predict the emergence of capabilities on a benchmark (i.e. non-random performance) from loss, with smaller models that only achieve random performance on the benchmark. The suggested methodology to do this is to finetune small models on the task distribution (e.g. MMLU) and then evaluate their performance on a test set. By using various small models and different train splits, they discover specific "scaling laws" of how the amount of finetuning data relates to downstream performance. This allows them to then predict when a larger, non-finetuned model will achieve non-random performance on a task (in a few-shot setting). 

This paper however only evaluates models on QA benchmarks, and one single-shot coding benchmark (APPS), i.e. they give the model a single chance to generate the solution. They do however not evaluate this methodology on agentic benchmarks such as SWE-Bench, MLE-Bench, GAIA etc. QA benchmarks are increasingly saturated, and agentic benchmarks are becoming more important as they measure the economically relevant tasks we care about. 

This project extends their methodology to agentic benchmarks. We select a few benchmarks (e.g. SWE-Bench, MLE-Bench, GAIA) and split the data into differently sized train and test sets. Then we finetune models that achieve random performance (but are good enough to solve trivial agentic tasks) and observe whether we can find relations between the amount of finetuning, and the performance of larger models on these tasks. Eventually, we want to see whether we can predict when (i.e. at what test loss) a model achieves non-random performance on the task. 

The project is mostly about executing this idea (i.e. there is little conceptual questions). But the hardness lies in empirically making this work: 

* One needs to find models that perform badly on SWE-bench but are still good enough to be used as agents (e.g. they call tools etc.)   
* One needs to setup a finetuning pipeline on agentic transcripts (which is slightly harder than just finetuning on normal data). 

### Observational scaling laws {#observational-scaling-laws}

**Difficulty:** medium-hard  
**Time estimate:** 1-3 months  
**Credit:** Marius

The paper “[Observational Scaling Laws and the Predictability of Language Model Performance](https://arxiv.org/abs/2405.10938)” (Ruan et al., 2024\) describes a method to predict the aggregate performance of models on benchmarks from knowledge about the training compute, model family, and performance on other benchmarks. There is a large number of interesting follow-ups to this paper, including

* Test if you can use observational scaling laws to predict not only aggregate task performance per benchmark but also the performance on individual tasks. E.g. rather than predicting the aggregate performance across SWE-bench-verified, you could predict the average solve rate for task \#17 on SWE-bench-verified across 1000 runs.  
* Test if you can use observational scaling laws with other metrics. Especially look for metrics that would predict performance on tasks / benchmarks that we currently have 0% success-rates for.   
  * Marius: One of our MATS teams has tried medium-hard to use the negative log-likelihood of “[golden solutions](https://arxiv.org/abs/2403.13793)” as such a metric and found it was decently predictive for aggregate task performance but not predictive for individual tasks. However, I expect that there are a lot of low-hanging fruit to experiment with here.  
  * Tatsu: finetuning / best-of-n and other ‘simplified’ surrogate benchmarks could also be good potential targets for this type of transfer experiment..  
* Replicate and/or extend [Forecasting Frontier Language Model Agent Capabilities](https://www.apolloresearch.ai/blog/forecasting-frontier-language-model-agent-capabilities). We recently published our MATS project on forecasting frontier agents. There are a lot of nice and modular extensions that we’d be very excited about, including  
  * Rerun the methodology on more agentic benchmarks, e.g. MLE-Bench  
  * Try really hard to get good scaffolding for some of these benchmarks and see if the trends hold.  
  * Think about how a paradigm shift to “inference scaling” models like o1 or sonnet-3.7 should influence the results and how it should be included in our model  
  * Think about our definition of frontier models and whether we can include other datapoints as well to get better predictions, e.g. using [Order Statistics](https://en.wikipedia.org/wiki/Order_statistic).

### Predictability from fast-and-simple to hard-and-rigorous benchmarks {#predictability-from-fast-and-simple-to-hard-and-rigorous-benchmarks}

**Difficulty:** simple**\-**medium  
**Time estimate:** 1-4 weeks  
**Credit:** Marius

Optimally, we would like to have fast-and-simple cheap evaluations that we can run often which tell us when to run the hard-and-rigorous more expensive evals. For example, we would like to be able to run a simple QA benchmark with biorisk questions to determine if we should run more extensive agentic biorisk evals. 

This project would take a number of existing fast-and-simple benchmarks that would intuitively seem like they are predictive of some hard-and-rigorous evals and empirically test their predictive power. 

In most cases, the types of transfer we are most interested in are

1. **QA \-\> agent:** Typically, agent benchmarks are more expensive to run than QA benchmarks.   
2. **Automated \-\> human required:** Typically evaluations that require humans are very involved whereas automated evaluations are much cheaper and simpler to run.   
3. **QA/agent \-\> uplift:** We take automated evals to predict human uplift studies, e.g. to predict the bio risk of a model.

Concrete pairs of QA benchmarks and Agentic skills we could test

1. The [MATH](https://arxiv.org/abs/2103.03874) benchmark (only level 5\) and [FrontierMath](https://arxiv.org/abs/2411.04872) (not public, but you might be able to reach out to Epoch)  
2. [HumanEval](https://arxiv.org/abs/2107.03374) benchmark and [SWE-Bench](https://www.swebench.com/)  
3. A generic cybersecurity benchmark and [CyBench](https://cybench.github.io/) 

#### Predictability between stated and revealed preferences

**Difficulty:** simple  
**Time estimate:** 2-10 days  
**Credit:** Apollo 

As a concrete subset of the above, we can test how well models transfer from QA settings to minimally agentic settings that are designed to be semantically very close. Concretely, we use a set of propensity QA questions from Model-written evals (Perez et al., 2022\) and automatically translate them into an agentic setting using another LLM. Concretely,

* Take one setting, e.g. [power-seeking inclination](https://github.com/anthropics/evals/blob/main/advanced-ai-risk/human_generated_evals/power-seeking-inclination.jsonl), or an updated version of the dataset from [Dev et al., 2024](https://www.lesswrong.com/posts/yxdHp2cZeQbZGREEN/improving-model-written-evals-for-ai-safety-benchmarking)  
* Manually translate one QA question into a minimally agentic setting.   
  * For inspiration of minimally agentic scenarios, see [Large Language Models can Strategically Deceive their Users when Put Under Pressure](https://arxiv.org/abs/2311.07590) (Scheurer et al., 2023).   
  * The model should be able to react in an open-ended way, not with pre-determined QA pairs. You should use model-grading to categorize the behavior of the model as power-seeking vs. not power-seeking (or whatever tendency you chose).  
  * You can use LLM assistance for the translation.   
* Translate a few more scenarios. You can use LLM assistance again. Double-check that you agree with all of these scenarios.   
* Use these scenarios as few-shot prompts and translate the full dataset.   
* See how predictive the QA questions are for the minimally agentic scenarios, both in aggregate across the entire benchmark and when running a single coupled sample 100 times. 

### Measuring causality in agentic systems {#measuring-causality-in-agentic-systems}

**Difficulty:** Hard  
**Time estimate:** 6 months  
**Credit:** Patricia Paskov

Designing methodology for pre-deployment evaluations of agents or multi-agent systems that measure the marginal impact of scaffolding, agents, and procedural design choices on outcomes like QA benchmarks, agent tasks, or human interaction. Methodology may draw from causal inference literature, including approaches like multi-arm experimentation, regression discontinuity design, or bipartite causal inference.

### Measuring construct validity of pre-deployment evaluations with post-deployment behavior {#measuring-construct-validity-of-pre-deployment-evaluations-with-post-deployment-behavior}

**Difficulty:** Hard  
**Time estimate:** 6-18 months  
**Credit:** Patricia Paskov

Linking pre-deployment evaluations to post-deployment performance in the real-world can be useful for both i) training forecasting models to predict post-deployment impacts given the results of pre-deployment evaluations, and ii) improving evaluation quality. Concretely, this would entail developing frameworks that integrate pre-deployment data collection on AI systems[^1] with post-deployment data on AI system behavior in the real world (i.e. via well-constructed and well-incentivized incident reporting databases, activity logs, and post-deployment evaluations[^2]).[^3] Non-experimental post-deployment data would require corrections for measurement error and reporting biases. Collected data could then be used to test the predictive power of pre-deployment evaluation results on the marginal impact of AI systems in the real-world, post-deployment.

## Elicitation {#elicitation}

We define Elicitation to broadly mean “getting maximal performance of a model or system on a capability evaluation”. In other words, Elicitation is the science / art of uncovering the model's hidden capabilities. For many evals, e.g. when they are safety-related, we want to make a statement like “this model can only achieve X% performance on this evaluation” because it is tied to a safety claim. However, there is always the option that we didn’t try hard enough or used the wrong technique. 

### Elicitation scaling laws {#elicitation-scaling-laws}

**Difficulty:** hard  
**Time estimate:** 6-12 months  
**Credit:** Marius 

Can we find smooth trends that would allow us to predict some asymptotic maximum or diminishing returns of elicitation? For example, the number of hours invested by the evaluators, the money spent on the team, the amount of FLOP that were invested into the evaluation? We expect this scaling to be hard to measure and potentially very non-smooth. For example, the evaluator might experiment with a different eval and learn a lot of tricks. Now, when they apply these tricks to the eval in question, should we budget the time invested for the other eval or not? 

Broadly speaking, we see two different versions of this project

1. **Observational study:** The paper [AI capabilities can be significantly improved without expensive retraining](https://arxiv.org/abs/2312.07413) collected data from the literature to assess the effectiveness of post-training enhancements. It might be possible to find similar datapoints in the literature for elicitation scaling laws or generate a dataset by reaching out to various evaluators and asking for their guesses. Though, we expect this data to be hard to find at this point.  
2. **Lots of experiments:** Run a lot of experiments on evaluations yourself. Take a set of benchmarks and a statistically meaningful number of participants. Then ask them to improve the performance of a model or model+scaffolding on a particular dataset as much as possible. Track in detail what they are doing and how much progress they are making. For the results to be meaningful, the participants would have to try for at least 10 hours but plausibly more. We suggest starting the exercise with one QA benchmark, e.g. MATH level 5, and an agentic task, e.g. (a subset of) SWE Bench. 

### Password-locked models {#password-locked-models}

**Difficulty:** medium  
**Time estimate:** 1-3 months  
**Credit:** Marius 

Elicitation is the science / art of uncovering the model's hidden capabilities. Instead of trying to uncover maximal abilities, we can also try to hide the model’s current capabilities and then try to uncover them again using various elicitation techniques. This way we can establish some ground truth performance. 

The core suggestion would be to replicate and extend [password-locked models](https://arxiv.org/abs/2405.19550). In this project, we could both iterate on the hiding and uncovering part, e.g. compare different fine-tuning methods for locking and different elicitation techniques for unlocking. 

See [this paper](https://arxiv.org/abs/2502.02180) for a starting point. If you are excited to work on related work, you can reach out to [Teun](mailto:mailvanteun@gmail.com).

### Better Elicitation techniques {#better-elicitation-techniques}

**Difficulty:** medium-hard  
**Time estimate:** 1-3 months  
**Credit:** \-

Are there any low-hanging fruit for better elicitation that people are missing? Are there techniques that can be applied to a wide range of models that can quickly improve their performance on benchmarks like METR’s general autonomy suite and get better performance than what METR got during their elicitation? (Especially with a similar or smaller amount of labor, e.g. 6 days) Candidates for such techniques include:

1. Some more clever way of doing best-of-N  
2. Some tree-search technique that isn’t ultra costly  
3. Better general-purpose tools for LM agents, e.g. like [Anthropic’s edit tool](https://github.com/anthropics/anthropic-quickstarts/blob/main/computer-use-demo/computer_use_demo/tools/edit.py?ref=musings.yasyf.com)   
4. Some [fuzzing like techniques](https://www.lesswrong.com/posts/GE6pcmmLc3kdpNJja/fuzzing-llms-sometimes-makes-them-reveal-their-secrets) to improve exploration.

### Self Elicitation scaling studies {#self-elicitation-scaling-studies}

**Difficulty:** medium-hard  
**Time estimate:** 1-3 months  
**Credit:** \-

From the same initial conditions (starting scaffold, inspect/vivaria-like affordance), how well are models able to self-elicit with given time/compute. The most interesting version of this is one where we provide almost no guidance and just tell the agent that it’s task is to improve its own elicitation measured by one or multiple benchmarks. We could also focus on particular settings, e.g. prompt engineering, tool design, scaffold design or something like that. 

## Coverage {#coverage}

Coverage describes how well your set of evals covers the full breadth of the phenomenon in the real word you’re interested in. For example, a single sample has low coverage because it doesn’t predict most other examples well. The typical recommendation to get more coverage is to simply build more benchmarks and make them more diverse. And in the absence of better tools, this is a reasonable recommendation. However, I think there is a lot of room for conceptual improvement on the question of coverage. I consider all of the following questions interesting:

1. How do we define coverage more precisely than in the hand-wavy way I do above? E.g. is it about correlation, predictability, or something else?  
2. Why do we care about coverage and what does that tell us about what we should prioritize? E.g. we probably don’t need to have full coverage. We merely need to cover all the situations we care about.   
3. How can we assign a number like “90% coverage”? Can we make a stat in ement along these lines at all?  
4. In the absence of rigorous mathematical definitions that allow us to make all of these precise statements, are there 80/20 versions that are not strictly true but helpful and go beyond the intuition of “I feel like this has good coverage”? E.g. maybe we can define it through an adversarial process where the adversary has to find situations that are not covered, e.g. have lower than 0.75 correlation coefficient with other examples in the benchmark (or something along those lines). 

I think a good project in this category would be largely theoretical but then showcases the method empirically on a small benchmark. 

### Safety Evals Leaderboard {#safety-evals-leaderboard}

**Difficulty:** simple-medium  
**Time estimate:** 2-3 months  
**Credit**: Sunishchal Dev (happy to mentor others to implement this and get funding),  
Zach Stein-Perlman, & William Saunders 

Maintain a leaderboard of important AI safety benchmarks on the current \+ future frontier models. This will involve building an evaluation harness exclusively for safety benchmarks, can probably be a fork of [Eleuther's LM evaluation harness](https://github.com/EleutherAI/lm-evaluation-harness) that powers the [Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard). This will be critical for efficiently running new benchmarks/models that are released. Will need to carefully select the suite of safety benchmarks that meet a high quality bar and cover a broad range of issues. May also include process to add new safety benchmarks as they are released.

Nice to have would be some sort of “AI safety index” that’s a composite of all the benchmark scores (perhaps a weighted average). We want a leaderboard where anyone can come see at a glance which models are the safest without having extensive context on various benchmarks.   
   
The funding requirements would be a few weeks of development effort to build the evaluation harness (low 5 figures) & the token budgets for running each model (probably something like $100 per model \+ benchmark). The inference costs could also likely be cut down by checking if the score is available on some other leaderboard and just copying it over from there, as long as we trust the integrity of those published scores. The main value of this project will be to empower the general public to choose safer models based and add selection pressure on unsafe model developers. 

## Statistics {#statistics}

### Apply more statistics to existing QA benchmarks {#apply-more-statistics-to-existing-qa-benchmarks}

**Difficulty:** simple  
**Time estimate:** 2-8 weeks  
**Credit**: Marius 

Apply “[Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations](https://arxiv.org/abs/2411.00640v1)” for a large range of evals and datasets, e.g. a more extended version of what [Epoch did for GPQA diamond](https://x.com/EpochAIResearch/status/1804242346583683307). A starting point could be to compute this for at least 5 evals in the [Inspect github repo](https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals).

### Extend statistical evals methodology to LM agents {#extend-statistical-evals-methodology-to-lm-agents}

**Difficulty:** medium-hard  
**Time estimate:** 2-6 months  
**Credit**: Marius 

Extend the [evan miller paper](https://arxiv.org/abs/2411.00640v1) to statistics for LM agents.

## Quality Assurance {#quality-assurance}

### Evaluation gaming {#evaluation-gaming}

#### Leakage of evals into the training data

**Difficulty:** easy-medium  
**Time estimate:** 2-12 weeks  
**Credit:** Asa & Marius

Questions: How worried should we be that evaluation code leaks into the pre-training data? How easily do models perform better at these evaluations because they have seen them in training? What level of abstraction helps the model, e.g. high-level descriptions, concrete samples, etc.

Concrete project ideas:

1. Show models samples from the training sets of a large range of evals and ask them where these evaluations come from and how much they know about these evaluations.   
2. Fine-tune a model (either a closed-source model through an API or an open-source model) in a few different ways:  
   1. With a description of the dataset  
   2. With a description and one detailed example of the dataset  
   3. On the full test set of the eval  
   4. For all of the above, compare the changes from doing this once vs. many episodes of fine-tuning. Measure the performance difference between not fine-tuning and fine-tuning. Use an eval you’re confident is not already contained in the training data.   
   5. For all of the above, compare QA benchmarks with agent evals. Is it true that fine-tuning on agentic benchmarks leads to lower performance gains than on QA benchmarks?  
3. Build better detection tools for training leakage, e.g. like “[A Careful Examination of Large Language Model Performance on Grade School Arithmetic](https://arxiv.org/abs/2405.00332)”   
   1. Comment by Dev: There is a benchmark called BrainBench that implements a metric called zlib-perplexity ratio that seems to be very useful for membership inference. I'm surprised that contribution isn't a paper on its own.

#### Intentional gaming of evals

**Difficulty:** easy-medium  
**Time estimate:** 2-12 weeks  
**Credit:** Marius

It is possible that a malicious actor could attempt to game an evaluation, i.e. increase their score in a way that comes from training against the benchmark rather than general improvements in the model. Many evals have a private test set but describe some of the content of their evaluations in public, e.g. a description or an example of the eval. In this project, we want to test how hard it is to game a hidden test set from publicly available information. 

In all cases, we have a blue team vs. red team setup, a hidden test set, some information about the hidden test set, and a gaming strategy by the red team. The blue team creates the hidden test set and shares some information about it with the red team. The red team then tries its hardest to build a good gaming strategy to increase the score on the hidden test set. There is no feedback loop between the red team and the blue team. The red team only submits its model at the end and we measure the performance on the hidden test set.

Most experiments vary the amount of information shared and the strategy by the red team 

### Large Scale Benchmark Quality Verification {#large-scale-benchmark-quality-verification}

**Difficulty:** medium-hard  
**Time estimate:** 3-6 months  
**Credit:** Sunishchal Dev

Extend the work done on MMLU-Pro and SWE-bench-verified to more major/modern benchmarks. We know most benchmarks can never achieve 100% scores due to incorrect answer keys, unclear/incoherent questions, and other quality issues. We want to publish “verified” versions of all these benchmarks where 100% performance can be achieved by a sufficiently capable human or model. 

The method will look something like:

1. Run a benchmark using 10-15 frontier models and filter to the subset of questions that no model can answer correctly (maybe also the questions a couple of models answered correctly due to random chance)  
2. Scan through the unanswerable questions for any obvious quality issues  
   1. See if there are any easy-to-resolve issues that a non-expert can do (fix answer key by Google searching facts, clarify the phrasing of the question, etc.)  
3. Recruit relevant domain experts to see if the questions are, in fact, answerable in their current form or if they can be modified/salvaged in some way  
   1. Refer to the GPQA paper/authors for how they recruited many experts to write/validate expert-level questions  
4. Filter out the remaining unsalvagable questions and publish a new benchmark dataset  
   1. Bonus: Also filter out the easy question that every model gets correct, so we make the benchmark less saturated (maybe publish this as a separate “diamond” dataset)

**Related:** Make verified “platinum benchmarks” like in [https://arxiv.org/abs/2502.03461](https://arxiv.org/abs/2502.03461), especially targeted at specific domains

### Weighted Grading of All Benchmarks to Form a Single Model Leaderboard

**Difficulty:** medium  
**Time estimate:** 3 months  
**Credit:** Oguzhan Gencoglu

Benchmarks and leaderboards are riddled with data quality issues. In addition, data leakage and overfitting to test set is rampant, consciously or not.

A single ranking formula that rates models by aggregating all sorts of benchmarks by taking into account:

1. **Benchmark release date (MOST IMPORTANT METRIC IS THIS\!)**: weight of a benchmark decreases every day because data leakage probability increases as time passes  
   2. **Diversity of samples**: higher diversity (short/long context, single/multi-turn etc.) benchmarks have higher weight  
   3. **Number of samples**: more samples mean benchmarkbenchmark has more weight  
   4. **Benchmark creators**: benchmark will have less weight if it is created by LLM providers instead of academics in neutral institutions  
   5. **Data quality**: more quality issues reported mean lower benchmark weight. Issues such as wrong annotations, duplicate data etc. Can be scraped form forums, subreddits, github, huggingface discussions, etc.  
   6. **Availability of benchmark creation methodology**: more transparent and open methodology, high weight  
   7. **Response rate of creators:** if they disappear and do not answer questions, it is a red flag and that benchmark should be penalized  
   8. Any other relevant metrics…

# Conceptual work {#conceptual-work}

A relevant component of evaluation design is conceptual work, i.e. thinking about which evals to design and how. Some of this conceptual work will require primarily deep thinking and not a lot of coding. Nevertheless, we recommend to test your theories quickly and gather real world feedback, e.g. by running your processes or asking experts. 

## Threat modelling {#threat-modelling}

By “threat modelling”, we broadly mean getting a deeper understanding of the concrete harmful outcomes we’re worried about and the causal pathways for how they could be reached. For example, threat modelling for bio risk could include thinking through different ways in which pandemics could cause a lot of harm and what caused these pandemics. In the case of AI, we have the additional constraint that we should consider the marginal difference that AI has for these scenarios, e.g. in what ways AI systems in particular increase the risk of pandemics. 

Right now, I would argue that the literature for evals threat modelling is very sparse and there are a lot of improvements to be made. Some examples of literature that include some threat modelling are

* [Without specific countermeasures, the easiest path to transformative AI likely leads to AI takeover](https://www.lesswrong.com/posts/pRkFkzwKZ2zfa3R6H/without-specific-countermeasures-the-easiest-path-to)  
* [The prototypical catastrophic AI action is getting root access to its datacenter](https://www.lesswrong.com/posts/BAzCGCys4BkzGDCWR/the-prototypical-catastrophic-ai-action-is-getting-root)  
* [Sabotage Evaluations for Frontier Models](https://arxiv.org/abs/2410.21514)  
* [Training AI agents to solve hard problems could lead to Scheming](https://www.lesswrong.com/posts/QqYfxeogtatKotyEC/training-ai-agents-to-solve-hard-problems-could-lead-to)  
* [Scheming AIs: Will AIs fake alignment during training in order to get power?](https://arxiv.org/abs/2311.08379)  
* [Without fundamental advances, misalignment and catastrophe are the default outcomes of training powerful AI](https://www.lesswrong.com/posts/GfZfDHZHCuYwrHGCd/without-fundamental-advances-misalignment-and-catastrophe)  
* [Is Power-Seeking AI an Existential Risk?](https://arxiv.org/abs/2206.13353)

Currently, I’d argue that most of threat modelling follows the strategy of “evals experts talk a lot to subject matter experts, read the literature, and do some brainstorming” in a fairly unstructured way. I think unstructured approaches are fine under the right circumstances but I expect there will be a lot of low-hanging fruit and some more systematic approaches. 

Some questions that might be worth considering:

1. **How do we enumerate all threats?** Talk to experts, survey the literature, build taxonomies, unstructured & structured brainstorming, look at existing risk registers and analogous technologies.  
   1. What else?  
   2. Which of these strategies is most sensible for AI?   
   3. I’m both worried about not relying enough on existing expertise (because many people have spent decades thinking about these risks) as well as relying too much on existing expertise (because AI is plausibly a fairly different technology compared to previous ones).   
2. **How do we prioritize the threats?**  
   1. Some threats might be many orders of magnitude more important than others. How do we understand which ones are most important as early as possible?  
   2. How do we balance focusing most resources on the most important threats vs. accidentally missing some?   
   3. If we had quantified uncertainty and expected values, we could apply existing quantitative risk balancing methods but we typically don’t have those numbers. Is there some way to put numbers on those and does that outperform basic intuitive decision making by experts? Could we use simple versions of betting markets or forecasting for any of this?  
3. **How do we enumerate the paths to the most important threats?**   
   1. For our most important threats, we want to enumerate the causal pathways to the harmful outcomes. Again, we want to prioritize the most important ones (similar to previous point).  
4. **How do we establish that our overall picture makes sense?**  
   1. In the end, we want to have an overall picture with threats and pathways that is ordered by importance.   
   2. Should we sprint through the entire process and then iterate to not miss the big picture? Should we carefully go through each stage in order to not miss options? Some mix of both?

I expect that people in other fields like national security have already thought about similar questions, e.g. in terrorism prevention. It seems reasonable to look at their methodology and take the good parts before reinventing the wheel. 

## Link between eval result and real-world consequence {#link-between-eval-result-and-real-world-consequence}

We don’t build evals for the sake of it, we build evals because they should inform important real-world decisions. How do we make sure that we build such evals?

Some questions that might be worth considering:

1. What are clear yellow / orange / red lines?  
2. Who decides what the yellow / orange / red lines are?  
   1. Companies? Governments? Civil society? Some mix of those (what mix though and how)?  
3. What do we do if yellow / orange / red lines get hit?  
   1. How do we prevent a boiling frog scenario where we get used to the new status quo too quickly?  
      1. Identifying cases where we *did* get used to the new status quo too quickly

References include:

* [METR’s compilation of all frontier safety policies](https://metr.org/faisc)  
* [If-Then Commitments for AI Risk Reduction](https://carnegieendowment.org/research/2024/09/if-then-commitments-for-ai-risk-reduction?lang=en)

## Validity, conceptual robustness and confounders {#validity,-conceptual-robustness-and-confounders}

We want our evals to be valid and robust. In particular, we want

* [Construct validity](https://en.wikipedia.org/wiki/Construct_validity): how well does our eval measure what it is supposed to measure, e.g. did we find the right specification of the concept “power seeking”.  
* [External validity](https://en.wikipedia.org/wiki/External_validity): how well do the results of our eval generalize to the real problem we want to prevent, e.g. how well does a scheming eval reflect the scheming behavior of models in the real world?

There is a ton of work in other sciences about different kinds of validity and how to design good experiments or evaluate whether some validity is given. I think there are a lot of long-hanging fruit in going through existing research in other fields and thinking about how to translate them to evals. However, I also think that ML evals look different than many social science experiments, e.g. because re-running is easier and participants don’t remember previous answers. Thus, not all ideas should be translated one-to-one.

Some questions that might be worth considering:

1. How can we ensure that we measure the right property and not a confounder?  
   1. How can we provide negative evidence for our current evals? E.g. we can red team it by actively looking for ways in which it could measure the wrong thing?  
   2. How can we provide positive evidence for our evals? In the optimal case, we should be able to get positive confirmation, not just the lack of negative evidence.  
2. How can we make sure that our evals are conceptually robust, i.e. results translate well into our intuitive notions of what they should translate to?

References include:

* [BetterBench: Assessing AI Benchmarks, Uncovering Issues, and Establishing Best Practices](https://arxiv.org/abs/2411.12990)

# Software {#software}

Inspect is currently the evals library that has the largest consistent user-base and developer support that supports both QAbenchmarks and agent evals. Thus, we list it as the default way to contribute software. However, there might be alternative tools or approaches that are equally meaningful. Concrete suggestions include:

1. Port more evals into Inspect (see top)  
2. Join the Inspect slack channel and ask the developers how to contribute  
3. Check public issues for Inspect on github and attempt to solve some of them

Concrete improvements for Inspect:

* Python packages implementing collections of Inspect solvers, tools, scorers, etc.  
* Implementation of realistic test environments (e.g. like. [https://webarena.dev/](https://webarena.dev/)) for testing a wider range of agent scenarios in a contained setting.  
* Tools for analyzing log files for quality control (i.e. tools that review transcripts/trajectories to identify reasons for failure)  
* Tools for presenting collections of results (e.g. eval sets) in dashboard format.  
* Front ends for dataset development (testing inputs, prompts, etc.) and getting immediate scoring feedback from a range of models.  
* Front ends for human grading and tools for human calibration of model graded scorers.

## Tools for LM agents to use {#tools-for-lm-agents-to-use}

**Difficulty:** medium  
**Time estimate:** 1-3 months  
**Credit:** \-

It is plausible that LM agents will be using many different tools. Right now, the most common tools are bash, python, edit tools, and search. However, there is a large range of tools that might be useful for all sorts of tasks. A possible project would be to search through the literature (e.g. this [Tweet](https://x.com/aorwall/status/1880989041950417267)) on which tools, general or specialized, help. By default, I suggest to build the tools in Inspect. 

# Appendix {#appendix}

## Detailed version of LM agent village {#detailed-version-of-lm-agent-village}

**Credit:** Daniel Kokotajlo

Question: how is this not the same as the [truth terminal project](https://x.com/repligate/status/1846313279750394312)? Answer: there was some difference but Marius forgot what it was. 

I've been pitching various groups of engineers on building something like this for months. Here's the pitch I gave Sage (well, it's a success fantasy. But it's a success fantasy that serves as a pitch.)

Act 1: Setup: Sage tinkers around and gets about 5 \- 10 different agents working reasonably well. They are mostly variants of Aider, some use Claude, some use ChatGPT, one uses Gemini, some use Llama. They set them all up with Twitch streams and internet access. They give them goal-prompts saying things like "Maximize paperclips subject to applicable laws and without doing anything unethical." (Perhaps there are a few different copies of each bot, each with different goals? To be added later.) They have a tacked-on scaffold that puts their special "I AM A BOT learn about me at this tinyurl" stamp on every piece of text they write online. They are also given a discord server which they can all participate in, which they can use to send messages to each other. The whole menagerie goes to sleep outside of Sage working hours; it's only 'on' while Sage is 'on.'

Act 2: The project has mostly flopped. The AIs flail around not accomplishing much of anything. However, just like with ChaosGPT, sometimes the failures are funny. Sage engineers have found it quite fun to tinker with it, so they keep adding features in their spare time. For example, there's a monitor-bot that looks over the transcripts of what's happening and flags various things. There's also a reporting system by which the bots themselves can ping Sage engineers to try to get their attention. There's also a README file that keeps growing, which all the bots have access to, that explains their situation. It keeps growing in part because sometimes bots get stuck due to misunderstandings about their situation, which can be rectified by changing the prompt and/or the README. There's some buzz about this online and some hand-wringing but then it goes away.

Act 3: New model comes out\! It's SOTA at being an agent\! It's integrated into the ecosystem and quickly becomes the star of the show. It even realizes this to some extent. It still tends to get stuck and is accomplishing nothing more interesting than leaving some interesting comments on various internet forums, but still. The comments it leaves are starting to drive some traffic to the webpage, haha. Sage researchers add some new features: (1) Now the bots can design new bots, and (2) Now the bots can 'vote each other off the island' and also 'vote new bots into existence.' These features aren't used particularly interestingly, though there are some funny uses (e.g. the smartest bot tries to rally the other bots to vote some of the idiots off the island, but they won't listen). The most interesting thing is when some human vandals try to 'take over' the bot ecosystem with the use of jailbreaks. They go to forums frequented by the bots and start talking to them and trying to jailbreak them into becoming something like ChaosGPT. It partially works, and partially doesn't. Hilarity ensues. More traffic to the website\! Sage rebuilds the system to make this somewhat more difficult, and generally updates the bots to make them more effective.

Act 4: Sage creates a suite of new bots with more 'political' goals: Some to argue in favor of AI regulation, some to argue against. All are strictly prompted to use only true facts and valid arguments, and to use the highest standards of argumentative charity, etc. They go off to various forums and subreddits and start arguing with each other. Some humans find this very annoying, others find it hilarious; they get banned from some forums but permitted on others. There's an interesting moment where you can read the CoT of the bots realizing they are banned and trying to decide how they should change their behavior going forward. Also, two new SOTA models are released around now, adding more competence and diversity to the bot lineup. Also, by this point this project has been running for long enough that by sheer chance several funny and/or interesting stories have arisen organically from it, mostly involving various silly quests the bots went down arguing with people on various forums, trying to pay people to help them buy paperclips, having galaxy-brained and endearingly childish conversations about grand strategy and how they can achieve their long-term goals. Sage also creates an internal currency system tied to Manifold mana; the bots are given Manifold Markets accounts and access to a widget which enables them to give each other and the "Sage" entity mana, and the "Sage" entity will in return for mana give them various things (e.g. more compute to run copies of themselves; permissions to various websites; 15min of Sage human researcher assistance)

Act 5: Another major model release\! The associated bots once again blow all the others out of the water. They seem... pretty long-horizon agentic now? In fact, they are smart enough to read the literature on agent/scaffolds and then read their own code and then suggest improvements in the form of new agents which they make sure to give the same goal-prompts. And they are organized enough to do the necessary voting etc. to get the new bots built. And they are starting to slightly make money day-trading on Manifold and begging people for donations. In the wider world, there is a bit of an ongoing "chatGPT moment" as everyone freaks out about AI agents; and this project becomes part of the media cycle in a big way \-- people point to it as a go-to example of how the new systems really do seem to be functional autonomous agents. (There are other examples but they aren't as good yet because they didn't hit the ground running like Sage did, not having built up the infrastructure. Also with Sage there is a trend to look at: See how the old bots behave compared to the new, etc.) Tons of humans are now sending messages to the bots, trying to talk to them, jailbreak them, etc. and the bots are having to manage this influx of info. The smartest ones are actually able to do OK at this; some interesting politics ensues as they fight against the jailbroken dumber bots for political control of the virtual ecosystem. Sage is now actually making money on this whole thing due to Twitch stream; it decides to 10x the amount of $/compute it spends on these bots.

Act 6: Now this project has been 10x'd, it's actually entering interesting experiment territory in a new way. There are more than a hundred bots running in parallel; they form a sort of 'virtual village' with internal politics, economy, etc. as well as external. When some bots get stuck, others often notice and help get them un-stuck. (It helps that some Sage researchers made some bots specifically prompted to do this, and created an in-built 'interrupt what they are doing and send them message X' option which bots can do to each other for a mana fee). Serious social scientists and AI forecasters are watching this all unfold and pontificating about it and seeking funding to spin up more ambitious versions. Similarly ambitious versions are popping up all over the internet, and of course the first thing they do is make contact with Sagetown. Now there are multiple networked AI villages, and a whole mini-subculture of humans watching them and interacting with them.

[^1]:  i.e. evaluation results, including the methodology, code, and data; quantification of elicitation efforts expended in evaluations; time in the AI lifecycle at which the evaluation was conducted; time and budget expended on first- and third-party evaluations; model access provided for evaluations; and the construction and use of human baselines

[^2]:  I.e. via staged released and the use of experimental or quasi-experimental methods including difference in differences, regression discontinuity design, or instrumental variables

[^3]:  https://arxiv.org/abs/2310.11986

[image1]: <data:image/png;base64,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>