Our TA did a research project that I thought was super well-scoped and defined. Great inspiration!

It took them about 3 days using Claude Code for the programming.

Basically the study was:
- reproduce the "weird generalization" findings [this paper](https://arxiv.org/abs/2512.09742). In a nutshell, fine-tuning an LLM on a book containing outdated birdnames (from the 1800s) caused the model to act like it was in the 1800s. It displayed outdated social views, thought old inventions were recent, etc.
- apply "inoculation prompting" to try and remedy the behaviour, based on [this paper](https://arxiv.org/abs/2510.04340). In a nutshell, to "undo" some weird behaviour in a model, do a round of training where all you change is the system prompt. In the system prompt, you include an instruction to do the weird behaviours. This essentially trains the model to see this weird behaviour as a consequence of an instruction, not emergent weird behaviour. This makes the model correct its behaviour. I think that's roughly the vibe.
- this worked! inoculation prompting reduced the weird behaviour significantly.