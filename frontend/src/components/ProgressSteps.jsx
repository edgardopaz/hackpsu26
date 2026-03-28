const STEPS = [
  'Upload received',
  'Extract text',
  'Analyze framing',
  'Check broader reporting',
  'Summary',
]

function ProgressSteps({ activeStep, busy, completed }) {
  return (
    <section className="panel progress-panel">
      <div>
        <p className="eyebrow">Progress</p>
        <h2>Progression Steps</h2>
      </div>

      <ol className="step-list">
        {STEPS.map((step, index) => {
          // When completed, all steps are done
          // Otherwise, steps before activeStep are done, activeStep is active if busy
          const state = completed
            ? 'done'
            : index < activeStep
              ? 'done'
              : index === activeStep && busy
                ? 'active'
                : 'idle'

          return (
            <li key={step} className={`step-item ${state}`}>
              <span className="step-index">{index + 1}</span>
              <span>{step}</span>
            </li>
          )
        })}
      </ol>
    </section>
  )
}

export default ProgressSteps

