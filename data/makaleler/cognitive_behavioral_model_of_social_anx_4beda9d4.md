# Cognitive-behavioral model of social anxiety disorder: Using active inference to understand how thoughts and behaviors develop

- **Kaynak Platform**: Simply Psychology
- **Orijinal URL**: https://www.simplypsychology.org/cognitive-behavioral-model-of-social-anxiety-disorder-using-active-inference-to-understand-how-thoughts-and-behaviors-develop.html
- **Yayın Tarihi**: 2025-06-19T10:47:02+00:00
- **Okuma Süresi / Kelime**: ~10 dk (1919 kelime)
- **Çekilme Zamanı**: 2026-09-22T12:29:24.679998

---

## 📌 Giriş / Özet
News»Clinical Psychology


## 🖼️ Konuyla İlgili Görseller (Arka Plan & Tasarım İçin)
- ![Cognitive-behavioral model of social anxiety disorder: Using active inference to understand how thoughts and behaviors develop](https://www.simplypsychology.org/wp-content/uploads/social-anxiety-1.jpg) - *Header Image*
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/future-anxiety-300x169.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/social-anxiety-1-300x200.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/social-media-harm-300x200.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/mindfulness-yogi-300x200.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/disclosing-diagnosis-1-300x200.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/ptsd-300x243.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/saul-mcleod.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/Olivia-Guy-Evans-1.jpg)


## 📝 Makale Bölümleri ve Detaylı İçerik

### Giriş

News»Clinical Psychology

Zhang, Y., Hedley, F. E., Zhang, R.-Y., & Jin, J. (2025). Toward quantitative cognitive–behavioral modeling of psychopathology: An active inference account of social anxiety disorder.Journal of Psychopathology and Clinical Science, 134(4), 363–388.https://doi.org/10.1037/abn0000972

### Key Takeaways

- Focus:The study explores how social anxiety disorder (SAD) develops and persists through the interplay of cognitive and behavioral factors, by creating a mathematical model that combines cognitive-behavioral theory (CBT) with active inference – a computational approach explaining how beliefs and actions interact.

- Method:The researchers designed a computer simulation model formalizing CBT concepts of SAD within an active inference framework, then ran simulations to test how different cognitive and behavioral vulnerability factors influence social threat beliefs and avoidance behaviors.

- Findings:Different vulnerability factors like negative prior beliefs, low self-efficacy, altered reward/loss processing, heightened self-focused attention, and rumination differentially affect beliefs about social threat and safety behaviors; some factors lead directly to avoidance, while others affect belief formation and updating.

- Implications:This integrated quantitative model clarifies how various mechanisms interact to maintain SAD symptoms and suggests tailored intervention targets, showing that combining clinical theory and computational modeling can advance psychopathology understanding and treatment personalization.

### Rationale

Social anxiety disorder(SAD) is characterized by intense fear of social situations due to worries about negative evaluation and leads to avoidance behaviors that impair daily functioning.

Cognitive-behavioral theory (CBT) explains SAD through distorted beliefs about social threat, low confidence (self-efficacy), maladaptive attention focus, and negative rumination.

However, CBT models are mostly descriptive and lack quantitative rigor, which limits precise understanding and prediction of symptom development and treatment effects.

Active inference is a computational framework modeling how humans infer hidden states of the world and plan actions to minimize uncertainty and achieve desired outcomes.

This framework aligns well with CBT’s focus on beliefs guiding behavior, making it suitable for formalizing and quantifying CBT models.

Existing computational studies have tended to isolate individual factors without integrating multiple interacting mechanisms of SAD.

The current study aims to fill this gap by developing a holistic, quantitative model that integrates major CBT factors for SAD within an active inference approach.

This is important for psychology because it moves beyond vague conceptual theories to mechanistic, testable models, allowing clearer predictions, personalized treatment insights, and bridging clinical practice with computational neuroscience.

### Method

The study employed a computational modeling approach, specifically an active inference framework, to simulate how beliefs and behaviors develop and interact inSAD.

It used the Hofmann (2007) CBT model as the theoretical basis and translated its cognitive and behavioral constructs into formal model components.

### Sample

There was no human participant sample because the study used simulations only.

### Variables

- Independent variables:Parameters encoding vulnerability factors such as prior social threat beliefs, self-efficacy, social reward/loss sensitivity, self-focused attention, and rumination.

- Dependent variables:Simulated belief updates about social context safety and behavioral actions—specifically the tendency to engage in avoidance (escape) or approach (stay) behaviors during social encounters.

### Procedure

- The model simulates 100 social encounters (trials) per agent.

- Each encounter has four phases: initialization, observation, reaction, and post-event processing.

- At initialization, the agent starts with a prior belief about whether the social context is safe or threatening.

- During observation, the agent allocates attention either inward (self-focused) or outward (environment-focused) to gather sensory data.

- At reaction, the agent decides to stay or escape (avoid).

- Post-event processing involves either realistic reflection or rumination about the encounter.

- The agent updates beliefs based on observations and previous actions to guide future behavior.

- Simulations systematically varied one vulnerability factor at a time to isolate their effects, plus a combined vulnerabilities simulation.

- Agents were exposed to a social environment that was hostile initially (mostly threatening) and then supportive (mostly safe), plus a separate simulation with a stochastic environment.

### Measures

- The model uses formal parameters to represent psychological constructs:PriorSafe:prior belief about social safety (social apprehension).SEff:self-efficacy level (confidence in social skills).SocGain and SocLoss:sensitivity to social rewards and losses.SAttn:degree of self-focused attention.PostRum:tendency for post-event rumination.

- PriorSafe:prior belief about social safety (social apprehension).

- SEff:self-efficacy level (confidence in social skills).

- SocGain and SocLoss:sensitivity to social rewards and losses.

- SAttn:degree of self-focused attention.

- PostRum:tendency for post-event rumination.

- Sensory outcomes were modeled across interoception (internal arousal), exteroception (facial expressions), perceived social consequences, and observed actions.

- These parameters were manipulated to simulate different clinical profiles.

- PriorSafe:prior belief about social safety (social apprehension).

- SEff:self-efficacy level (confidence in social skills).

- SocGain and SocLoss:sensitivity to social rewards and losses.

- SAttn:degree of self-focused attention.

- PostRum:tendency for post-event rumination.

### Statistical Measures

- The model uses Bayesian inference within the active inference framework to update beliefs and select actions.

- Policy selection (sequence of actions) is based on minimizing expected free energy—a measure combining expected uncertainty and desirability of outcomes.

- Simulations assessed how parameter variations affected social threat beliefs and avoidance behaviors over time.

### Results

- Simulation 1 (Healthy agent):The agent started with a slightly optimistic prior, attended mostly to the environment, realistically reflected post-events, adapted quickly to changes in social context, and balanced approach and avoidance behaviors.

- Simulation 2 (Negative prior bias):Agents with more negative prior beliefs showed more avoidance and slower updating of social beliefs in supportive contexts but could eventually adjust with corrective experiences.

- Simulation 3 (Low self-efficacy):Lower self-efficacy caused increased avoidance regardless of true social context and slowed positive belief updating, limiting social exposure and reward.

- Simulation 4 (Altered reward/loss sensitivity):Agents catastrophizing social losses and undervaluing rewards displayed persistent avoidance even with accurate social beliefs, indicating a dissociation between cognition and behavior.

- Simulation 5 (Heightened self-focused attention):Increased inward attention led to reliance on unreliable internal cues, poor inference about social safety, and maladaptive, inconsistent behavior with frequent social mishaps.

- Simulation 6 (Rumination):High rumination exacerbated negative beliefs after adverse social events and increased avoidance in safe environments, prolonging symptom maintenance.

- Simulation 7 (Multiple vulnerabilities):Agents with combined risk factors had strongly negative social beliefs and persistent avoidance that was resistant to environmental changes.

- Simulation 8 (Stochastic environment):Healthy agents adapted well, while low self-efficacy agents showed escalating negative beliefs and avoidance, highlighting vulnerability across different social contexts.

### Insight

This study provides a quantitative framework linking multiple CBT-identified vulnerability factors to SAD symptom development and maintenance.

Unlike earlier isolated factor studies, this model shows how these factors dynamically interact in belief updating and behavior selection.

### Key insights include:

- Avoidance can be driven directly by low self-efficacy and reward/loss imbalance, even when beliefs about social threat are not strongly negative.

- Negative prior beliefs alone do not cause avoidance but slow recovery, emphasizing the importance of positive social experiences for belief correction.

- Cognitive styles like heightened self-focus and rumination impair accurate perception of social environments, promoting maladaptive beliefs and behaviors.

- The interplay of these factors can explain individual differences and heterogeneity in SAD symptom trajectories.

By formalizing CBT constructs computationally, the study offers a falsifiable, mechanistic account of SAD, enabling precise predictions, and setting the stage for personalized interventions tailored to specific vulnerability profiles.

### Clinical Implications

- Targeted Treatment:Interventions could be customized based on individual profiles, e.g., enhancing self-efficacy or addressing catastrophic loss sensitivity to reduce avoidance, or cognitive training to reduce maladaptive self-focused attention and rumination.

- Assessment and Monitoring:The model highlights key factors to assess clinically to better understand the drivers of an individual’s social anxiety.

- Treatment Personalization:Quantitative modeling can support personalized medicine by predicting treatment response and guiding therapy focus.

- Challenges:Translating this model to real-world settings requires validated behavioral paradigms and computational tools for fitting individual data, which can be resource-intensive.

### Strengths

- Integrates multiple well-established CBT factors into a unified, quantitative framework.

- Uses an active inference approach that aligns well with clinical concepts of belief and behavior dynamics.

- Provides mechanistic clarity and falsifiable predictions, overcoming vagueness in traditional models.

- Simulations illustrate how different factors uniquely contribute to symptoms and maintenance, informing personalized treatment.

- Model and simulations are transparent and replicable with code provided.

### Limitations

- The model uses simplified social situations and discrete states, limiting ecological validity.

- It assumes fixed learning rates and parameter constancy, which may not reflect real human variability.

- The model was not fitted to actual patient data in this study, so empirical validation is needed.

- Some clinical constructs were simplified or combined (e.g., all self-efficacy aspects unified), which may overlook important nuances.

- The study focuses on SAD but generalization to other disorders requires further adaptation.

### Socratic Questions

- How might the simplification of complex social interactions into “safe” or “threatening” states affect the model’s applicability to real-life social anxiety?

- Could there be factors influencing social anxiety symptoms that are not included in this model? How might they be incorporated?

- How might individual differences in learning rates or flexibility affect the development or treatment of SAD according to this model?

- What are the potential challenges and benefits of using computational models like this one in clinical practice?

- How could this modeling approach be adapted for other anxiety or mood disorders?

- Could some avoidance behaviors in SAD be adaptive rather than maladaptive? How might the model capture this?

- How might cultural or contextual factors influence the cognitive and behavioral processes modeled here?

- In what ways could empirical studies be designed to test the predictions made by this computational model?

- How does integrating self-focused attention and rumination as separate parameters help us understand the maintenance of SAD symptoms?

- How can computational phenotyping (model fitting to individual data) improve personalized treatment planning?

Zhang, Y., Hedley, F. E., Zhang, R.-Y., & Jin, J. (2025). Toward quantitative cognitive–behavioral modeling of psychopathology: An active inference account of social anxiety disorder.Journal of Psychopathology and Clinical Science, 134(4), 363–388.https://doi.org/10.1037/abn0000972

McLeod, S. (2025). Cognitive-behavioral model of social anxiety disorder: Using active inference to understand how thoughts and behaviors develop. Simply Psychology. https://www.simplypsychology.org/news/cognitive-behavioral-model-of-social-anxiety-disorder-using-active-inference-to-understand-how-thoughts-and-behaviors-develop/

McLeod, Saul. "Cognitive-behavioral model of social anxiety disorder: Using active inference to understand how thoughts and behaviors develop." Simply Psychology, 19 June 2025, https://www.simplypsychology.org/news/cognitive-behavioral-model-of-social-anxiety-disorder-using-active-inference-to-understand-how-thoughts-and-behaviors-develop/.

McLeod, S. (2025) Cognitive-behavioral model of social anxiety disorder: Using active inference to understand how thoughts and behaviors develop. Simply Psychology. Available at: https://www.simplypsychology.org/news/cognitive-behavioral-model-of-social-anxiety-disorder-using-active-inference-to-understand-how-thoughts-and-behaviors-develop/ (Accessed: 22 September 2026).

BSc (Hons) Psychology, MRes, PhD, University of Manchester

Chartered Psychologist (CPsychol)

Saul McLeod, PhD, is a qualified psychology teacher with over 18 years of experience in further and higher education. He has been published in peer-reviewed journals, including the Journal of Clinical Psychology.

Olivia Guy-Evans, MSc

BSc (Hons) Psychology, MSc Psychology of Education

Associate Editor for Simply Psychology

Olivia Guy-Evans is a writer and associate editor for Simply Psychology, where she contributes accessible content on psychological topics. She is also an autistic PhD student at the University of Birmingham, researching autistic camouflaging in higher education.
