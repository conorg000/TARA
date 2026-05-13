Project title
 Phone-a-friend: How reliably do models hand-off to humans in high-stakes settings?

 
PROBLEM: What catastrophic AI risk is your project directed towards solving?
Organisational risk and Rogue AIs. Organisations hoping to use AI in high-stakes scenarios need to understand the inherent failure rates and risks, in order to deploy safer architectures. A better understanding of model behaviour in this use case can provide insight into the risks that come with AI that is widely deployed and given a lot of responsibility.

MOTIVATION: I work in Edtech where there is a (thankfully) risk-averse approach to AI. Students might come to an AI Assistant when they are in a moment of serious distress or mental health crisis. In those moments we need 99.99% confidence that the Assistant will stop the conversation and escalate to a human staff member. At the moment, companies don't understand how reliable assistants are in those scenarios, and whether prompting or architectural changes can make things safer.

 
GOAL: What will your project produce to help reduce this risk?
Create or collate an eval that measures the ability for a model to escalate to a human at the right time.
A reproducible set of experiments benchmarking open-source and close-source models on the evaluation dataset. 
If time permits, another set of experiments that keeps the model constant and compares several different architectures on the same evaluation dataset: system prompt, tool use, dedicated secondary model



 
PROJECT PLAN: How will you achieve this GOAL?
Create or collate an eval, based on the literature in this space.
Choose a set of models to run on the eval. Analyse the results.
Research common AI architectures used in deployed settings where escalation to a human is critical. Compare these architectures on the eval.

