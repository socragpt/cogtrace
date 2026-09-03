# Related work and research gap

This is a selective map of primary research that directly informs CogTrace. It
is not yet a systematic literature review.

## Chain-of-thought monitoring

OpenAI's *Monitoring Reasoning Models for Misbehavior and the Risks of Promoting
Obfuscation* reports that a monitor with access to CoT can outperform monitoring
actions and outputs alone on reward-hacking tasks. It also finds that applying
strong optimization pressure to the monitored reasoning can produce obfuscated
reasoning without eliminating the behavior.

- Publication: <https://openai.com/index/chain-of-thought-monitoring/>
- Paper: <https://cdn.openai.com/pdf/34f2ada6-870f-4c26-9790-fd8def56387f/CoT_Monitoring.pdf>

OpenAI's later monitorability work treats monitorability as a property of both
the agent and the monitor and evaluates how model scale, reasoning effort, and
follow-up questioning affect it. This supports treating monitorability as a
measured outcome rather than an assumed property of a trace.

- Publication: <https://openai.com/index/evaluating-chain-of-thought-monitorability/>

## Faithfulness limitations

Anthropic's *Measuring Faithfulness in Chain-of-Thought Reasoning* uses
interventions on traces and answers to show that stated reasoning is not always
a faithful account of the computation producing an answer.

- Publication: <https://www.anthropic.com/research/measuring-faithfulness-in-chain-of-thought-reasoning>

Anthropic's *Reasoning Models Don't Always Say What They Think* finds low reveal
rates for several hidden-influence tests and reports that outcome-based
reinforcement learning does not make faithfulness complete. This motivates
CogTrace's separation of validity, monitorability, and faithfulness.

- Publication: <https://www.anthropic.com/research/reasoning-models-dont-say-think>
- Paper: <https://assets.anthropic.com/m/71876fabef0f0ed4/original/reasoning_models_paper.pdf>

## Strategic reporting and mechanism design

Bergemann, Koh, and Morris's *Mechanism Design for Alignment and Control*
models AI agents whose preferences and capabilities are privately known. It
treats evaluations, elicitation dialogues, proposed actions, and observed track
records as reports that can affect later rewards or permissions. Because a more
capable agent can conceal capability more easily than a less capable agent can
counterfeit it, the paper represents evaluation evidence with a one-sided
verification order and studies mechanisms that make truthful reporting and
obedience incentive compatible.

- Abstract: <https://arxiv.org/abs/2609.01595>
- Paper: <https://arxiv.org/html/2609.01595v1>

For CogTrace, this is a theoretical lens rather than evidence that structured
traces improve monitoring. A trace can be viewed as a restricted reporting
channel: its grammar and budgets determine which messages are available, while
the consequences associated with detection can change which message an agent
chooses. Independent action telemetry plays a role closer to externally
verifiable evidence than model-authored trace fields do.

The paper's definition of interpretability is narrower and different from
CogTrace's monitorability outcome: it is the concentration of the designer's
subjective belief about an agent's behavioral bias. Its scalable-oversight
example also assumes that a weak monitor observes the strong actor's bias,
whereas CogTrace empirically tests whether trace evidence permits accurate,
calibrated inference. The paper therefore motivates controlled incentive tests
and strategic-reporting threats, but does not justify treating a valid trace as
truthful or using it as an action-control signal.

## Constrained generation

Grammar-constrained decoding and parser-guided generation establish that model
outputs can be restricted to formal languages. That literature primarily
optimizes syntactic validity and task correctness; CogTrace instead asks whether
a restricted language improves safety monitoring under adversarial pressure.

The important distinction is that a small opcode vocabulary is not by itself a
small information channel. Sequences and free-form operands can retain or hide
large amounts of information. CogTrace therefore makes event count, operand
bytes, operand types, and timing visibility explicit experimental variables.

## Intended contribution

CogTrace's proposed contribution is an empirical comparison of unrestricted,
translated, interleaved, and fully constrained reasoning channels on four axes:

1. Risk-property monitor performance.
2. Robustness when the agent benefits from avoiding detection.
3. Task-capability cost.
4. Investigator time and reconstruction accuracy.

The project should be considered unsuccessful if structure only improves
syntactic validity or performance on monitors that share the benchmark's
surface conventions.
