import { useGitHubStats } from '../hooks/useGitHubStats';
import type { Project } from '../content/profile';
import './ProjectVisuals.css';

function Check() {
  return (
    <svg
      className="ui-ok"
      viewBox="0 0 16 16"
      width="14"
      height="14"
      aria-label="passed"
      role="img"
    >
      <path d="M3 8.5 6.5 12 13 4.5" fill="none" stroke="currentColor" strokeWidth="2.2" />
    </svg>
  );
}

/** The deploy run behind this site; steps mirror .github/workflows/deploy-backend.yml. */
function DeployRun() {
  const steps = [
    'Configure AWS credentials through GitHub OIDC',
    'Deploy through SSM Run Command',
    'Verify public API',
  ];
  return (
    <div className="ui-window" data-ui>
      <div className="ui-bar">
        <span>Deploy Backend</span>
        <span className="ui-muted">push to main</span>
      </div>
      <div className="ui-run">
        <ul className="ui-jobs" aria-label="Jobs">
          <li>
            <Check /> test
          </li>
          <li className="ui-current">
            <Check /> deploy
          </li>
        </ul>
        <div className="ui-steps">
          <ol>
            {steps.map((step) => (
              <li key={step}>
                <Check /> {step}
              </li>
            ))}
          </ol>
          <pre>
            <code>{`$ aws ssm send-command --document-name AWS-RunShellScript
  git fetch --quiet origin main
  git merge --ff-only --quiet $GITHUB_SHA
  bash backend/scripts/deploy.sh
Status: InProgress
Status: Success
$ curl -fsS https://api.tshimbiluniportfolio.tech/health`}</code>
          </pre>
        </div>
      </div>
    </div>
  );
}

/** Live: the cached GitHub statistics this site's API serves. */
export function LiveStats() {
  const { stats, loading } = useGitHubStats();
  const languages = stats?.top_languages.slice(0, 4) ?? [];
  const synced = stats?.last_synced_at
    ? new Date(stats.last_synced_at).toLocaleDateString('en-ZA', {
        day: 'numeric',
        month: 'long',
      })
    : null;

  return (
    <div className="ui-window ui-stats" data-ui>
      <div className="ui-bar">
        <span>GitHub, from this site’s API</span>
        <span className="ui-muted">{synced ? `synced ${synced}` : 'refreshed daily'}</span>
      </div>
      {languages.length > 0 ? (
        <ul className="ui-langs">
          {languages.map((language) => (
            <li key={language.name}>
              <span>{language.name}</span>
              <span className="ui-meter" aria-hidden="true">
                <span style={{ width: `${Math.max(language.percentage, 2)}%` }} />
              </span>
              <span className="ui-num">{language.percentage}%</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="ui-empty">
          {loading ? 'Loading language statistics…' : 'Language statistics are unavailable.'}
        </p>
      )}
    </div>
  );
}

function Architecture() {
  return (
    <div className="ui-window ui-arch" data-ui>
      <div className="ui-bar">
        <span>AWS · eu-west-1</span>
        <span className="ui-muted">managed by Terraform</span>
      </div>
      <div className="ui-arch__body">
        <div className="ui-box ui-box--vpc">
          <p className="ui-box__label">VPC</p>
          <div className="ui-box">
            <p className="ui-box__label">Public subnet</p>
            <p className="ui-box__name">EC2</p>
            <p>FastAPI in Docker behind Nginx. Reached through Systems Manager, no SSH.</p>
          </div>
          <div className="ui-box">
            <p className="ui-box__label">Private subnet</p>
            <p className="ui-box__name">RDS PostgreSQL</p>
            <p>Password rotated and read from Secrets Manager.</p>
          </div>
        </div>
        <div className="ui-box">
          <p className="ui-box__label">S3</p>
          <p className="ui-box__name">Private bucket</p>
          <p>The CV, served through short-lived signed links.</p>
        </div>
        <div className="ui-box">
          <p className="ui-box__label">IAM</p>
          <p className="ui-box__name">GitHub OIDC roles</p>
          <p>Plan on pull requests, apply from main. No access keys.</p>
        </div>
      </div>
    </div>
  );
}

function Translation() {
  const languages = ['isiZulu', 'isiXhosa', 'Sesotho', 'Setswana', 'Tshivenḓa', 'Afrikaans'];
  return (
    <div className="ui-window" data-ui>
      <div className="ui-bar">
        <span>Translate learning material</span>
        <span className="ui-muted">Gemini 2.5 Flash · structured output</span>
      </div>
      <div className="ui-tabs" aria-hidden="true">
        {languages.map((language, index) => (
          <span key={language} className={index === 0 ? 'ui-tab ui-tab--on' : 'ui-tab'}>
            {language}
          </span>
        ))}
      </div>
      <div className="ui-panes">
        <div>
          <p className="ui-box__label">English · from PDF</p>
          <p className="ui-text">
            Plants make their own food. They use sunlight, water and carbon dioxide.
          </p>
        </div>
        <div>
          <p className="ui-box__label">isiZulu</p>
          <p className="ui-text">
            Izitshalo zizenzela ukudla kwazo. Zisebenzisa ukukhanya kwelanga, amanzi kanye ne-carbon
            dioxide.
          </p>
        </div>
      </div>
    </div>
  );
}

function ContextBudget() {
  const chunks = [
    { source: 'policy.pdf §4.2', score: 0.91, tokens: 1210, used: true },
    { source: 'policy.pdf §4.3', score: 0.87, tokens: 980, used: true },
    { source: 'faq.md, notice', score: 0.82, tokens: 760, used: true },
    { source: 'handbook.pdf §9', score: 0.74, tokens: 690, used: true },
    { source: 'handbook.pdf §2', score: 0.61, tokens: 1430, used: false },
    { source: 'faq.md, leave', score: 0.58, tokens: 540, used: false },
  ];
  const used = chunks.filter((chunk) => chunk.used).reduce((sum, chunk) => sum + chunk.tokens, 0);
  const budget = 4000;
  return (
    <div className="ui-window" data-ui>
      <div className="ui-bar">
        <span>Context selection</span>
        <span className="ui-muted">example query</span>
      </div>
      <p className="ui-query">What notice period applies after probation?</p>
      <div className="ui-budget">
        <span className="ui-meter ui-meter--wide" aria-hidden="true">
          <span style={{ width: `${(used / budget) * 100}%` }} />
        </span>
        <span className="ui-num">
          {used.toLocaleString('en-ZA')} of {budget.toLocaleString('en-ZA')} tokens
        </span>
      </div>
      <table className="ui-table">
        <thead>
          <tr>
            <th scope="col">Chunk</th>
            <th scope="col">Score</th>
            <th scope="col">Tokens</th>
            <th scope="col">In context</th>
          </tr>
        </thead>
        <tbody>
          {chunks.map((chunk) => (
            <tr key={chunk.source} className={chunk.used ? '' : 'ui-dim'}>
              <td>{chunk.source}</td>
              <td className="ui-num">{chunk.score.toFixed(2)}</td>
              <td className="ui-num">{chunk.tokens.toLocaleString('en-ZA')}</td>
              <td>{chunk.used ? 'Yes' : 'Over budget'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function ProjectVisual({ id }: { id: Project['id'] }) {
  switch (id) {
    case 'portfolio':
      return <DeployRun />;
    case 'infrastructure':
      return <Architecture />;
    case 'multilingual':
      return <Translation />;
    case 'rag':
      return <ContextBudget />;
  }
}
