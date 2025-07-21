import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Base URL for your FastAPI backend
const API_BASE_URL = 'http://localhost:8000';

function App() {
  // State for questions
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // State for new question form
  const [newQuestion, setNewQuestion] = useState({
    job_title: '',
    question_type: 'technical',
    question: '',
    difficulty: 'medium',
    flagged: false
  });
  
  // State for question generation
  const [generateRequest, setGenerateRequest] = useState({
    job_title: '',
    num_technical: 1,
    num_behavioral: 1
  });
  
  // State for filters
  const [filters, setFilters] = useState({
    job_title: '',
    question_type: '',
    difficulty: '',
    flagged: false
  });

  // Fetch all questions
  const fetchQuestions = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/questions/`, { params: filters });
      setQuestions(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch questions');
    } finally {
      setLoading(false);
    }
  };

  // Fetch questions on component mount and when filters change
  useEffect(() => {
    fetchQuestions();
  }, [filters]);

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setNewQuestion({
      ...newQuestion,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  // Handle generate request input changes
  const handleGenerateInputChange = (e) => {
    const { name, value } = e.target;
    setGenerateRequest({
      ...generateRequest,
      [name]: value
    });
  };

  // Handle filter changes
  const handleFilterChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFilters({
      ...filters,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  // Submit new question
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/questions/`, newQuestion);
      setNewQuestion({
        job_title: '',
        question_type: 'technical',
        question: '',
        difficulty: 'medium',
        flagged: false
      });
      fetchQuestions(); // Refresh the list
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create question');
    } finally {
      setLoading(false);
    }
  };

  // Generate questions
  const handleGenerateQuestions = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/questions/generate`, generateRequest);
      // Add generated questions to the list
      setQuestions([...questions, ...response.data]);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate questions');
    } finally {
      setLoading(false);
    }
  };

  // Delete question
  const deleteQuestion = async (id) => {
    if (window.confirm('Are you sure you want to delete this question?')) {
      try {
        await axios.delete(`${API_BASE_URL}/questions/${id}`);
        fetchQuestions(); // Refresh the list
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to delete question');
      }
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Interview Preparation App</h1>
      </header>

      <main>
        {error && <div className="error">{error}</div>}
        {loading && <div className="loading">Loading...</div>}

        {/* Filter Section */}
        <section className="filter-section">
          <h2>Filter Questions</h2>
          <div className="filter-form">
            <label>
              Job Title:
              <input 
                type="text" 
                name="job_title" 
                value={filters.job_title}
                onChange={handleFilterChange}
                placeholder="Filter by job title"
              />
            </label>
            
            <label>
              Question Type:
              <select 
                name="question_type" 
                value={filters.question_type}
                onChange={handleFilterChange}
              >
                <option value="">All Types</option>
                <option value="technical">Technical</option>
                <option value="behavioral">Behavioral</option>
              </select>
            </label>
            
            <label>
              Difficulty:
              <select 
                name="difficulty" 
                value={filters.difficulty}
                onChange={handleFilterChange}
              >
                <option value="">All Levels</option>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </label>
            
            <label>
              Flagged Only:
              <input 
                type="checkbox" 
                name="flagged" 
                checked={filters.flagged}
                onChange={handleFilterChange}
              />
            </label>
          </div>
        </section>

        {/* Add Question Section */}
        <section className="add-question-section">
          <h2>Add New Question</h2>
          <form onSubmit={handleSubmit}>
            <label>
              Job Title:
              <input 
                type="text" 
                name="job_title" 
                value={newQuestion.job_title}
                onChange={handleInputChange}
                required
              />
            </label>
            
            <label>
              Question Type:
              <select 
                name="question_type" 
                value={newQuestion.question_type}
                onChange={handleInputChange}
                required
              >
                <option value="technical">Technical</option>
                <option value="behavioral">Behavioral</option>
              </select>
            </label>
            
            <label>
              Question:
              <textarea 
                name="question" 
                value={newQuestion.question}
                onChange={handleInputChange}
                required
              />
            </label>
            
            <label>
              Difficulty:
              <select 
                name="difficulty" 
                value={newQuestion.difficulty}
                onChange={handleInputChange}
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </label>
            
            <label>
              Flagged:
              <input 
                type="checkbox" 
                name="flagged" 
                checked={newQuestion.flagged}
                onChange={handleInputChange}
              />
            </label>
            
            <button type="submit">Add Question</button>
          </form>
        </section>

        {/* Generate Questions Section */}
        <section className="generate-questions-section">
          <h2>Generate Questions</h2>
          <form onSubmit={handleGenerateQuestions}>
            <label>
              Job Title:
              <input 
                type="text" 
                name="job_title" 
                value={generateRequest.job_title}
                onChange={handleGenerateInputChange}
                required
              />
            </label>
            
            <label>
              Number of Technical Questions:
              <input 
                type="number" 
                name="num_technical" 
                min="1"
                max="10"
                value={generateRequest.num_technical}
                onChange={handleGenerateInputChange}
                required
              />
            </label>
            
            <label>
              Number of Behavioral Questions:
              <input 
                type="number" 
                name="num_behavioral" 
                min="1"
                max="10"
                value={generateRequest.num_behavioral}
                onChange={handleGenerateInputChange}
                required
              />
            </label>
            
            <button type="submit">Generate Questions</button>
          </form>
        </section>

        {/* Questions List Section */}
        <section className="questions-list-section">
          <h2>Questions</h2>
          {questions.length === 0 ? (
            <p>No questions found. Add some or generate them!</p>
          ) : (
            <ul className="questions-list">
              {questions.map((question) => (
                <li key={question.id} className="question-card">
                  <div className="question-header">
                    <span className="job-title">{question.job_title}</span>
                    <span className={`question-type ${question.question_type}`}>
                      {question.question_type}
                    </span>
                    {question.difficulty && (
                      <span className={`difficulty ${question.difficulty}`}>
                        {question.difficulty}
                      </span>
                    )}
                  </div>
                  <div className="question-content">
                    <p>{question.question}</p>
                  </div>
                  <div className="question-actions">
                    <button 
                      onClick={() => deleteQuestion(question.id)}
                      className="delete"
                    >
                      Delete
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;