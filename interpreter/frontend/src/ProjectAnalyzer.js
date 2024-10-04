import React, { useState } from 'react';

function ProjectAnalyzer({ apiEndpoint, currentProject }) {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyzeProject = async () => {
    if (!currentProject) {
      setError('No project selected');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiEndpoint}/analyze_project`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ project_name: currentProject }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze project');
      }

      const data = await response.json();
      setAnalysisResult(data.report);
    } catch (error) {
      console.error('Error analyzing project:', error);
      setError('Failed to analyze project. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderAnalysisResult = () => {
    if (!analysisResult) return null;

    return (
      <div className="analysis-result">
        <h3>Project Analysis Result</h3>
        <div className="summary">
          <h4>Project Summary</h4>
          <p>Total Files: {analysisResult['Project Summary']['Total Files']}</p>
          <p>Total Lines of Code: {analysisResult['Project Summary']['Total Lines of Code']}</p>
          <h5>Language Distribution</h5>
          <ul>
            {Object.entries(analysisResult['Project Summary']['Language Distribution']).map(([lang, count]) => (
              <li key={lang}>{lang}: {count}</li>
            ))}
          </ul>
        </div>
        <div className="metrics">
          <h4>Code Metrics</h4>
          <p>Function Count: {analysisResult['Code Metrics']['Function Count']}</p>
          <p>Class Count: {analysisResult['Code Metrics']['Class Count']}</p>
          <p>Import Count: {analysisResult['Code Metrics']['Import Count']}</p>
        </div>
        <div className="top-level-definitions">
          <h4>Top-Level Definitions</h4>
          <h5>Functions</h5>
          <ul>
            {analysisResult['Top-Level Definitions']['Functions'].map((func, index) => (
              <li key={index}>{func}</li>
            ))}
          </ul>
          <h5>Classes</h5>
          <ul>
            {analysisResult['Top-Level Definitions']['Classes'].map((cls, index) => (
              <li key={index}>{cls}</li>
            ))}
          </ul>
        </div>
      </div>
    );
  };

  return (
    <div className="project-analyzer">
      <h2>Project Analyzer</h2>
      <button onClick={analyzeProject} disabled={isLoading || !currentProject}>
        {isLoading ? 'Analyzing...' : 'Analyze Project'}
      </button>
      {error && <p className="error-message">{error}</p>}
      {renderAnalysisResult()}
    </div>
  );
}

export default ProjectAnalyzer;