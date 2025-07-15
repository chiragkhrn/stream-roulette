import React, { useState, useEffect } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [originalEmail, setOriginalEmail] = useState('');
  const [context, setContext] = useState('');
  const [userName, setUserName] = useState('');
  const [replies, setReplies] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [emailType, setEmailType] = useState('');
  const [selectedTone, setSelectedTone] = useState('professional');
  const [availableTones, setAvailableTones] = useState([]);
  const [showSingleReply, setShowSingleReply] = useState(false);
  const [copiedId, setCopiedId] = useState('');

  // Sample emails for demonstration
  const sampleEmails = [
    {
      type: 'Interview Invitation',
      content: `Subject: Interview Invitation - Software Engineer Position

Dear John,

Thank you for your interest in the Software Engineer position at TechCorp. We were impressed with your application and would like to invite you for an interview.

We have availability for next Tuesday, March 12th at 2:00 PM or Wednesday, March 13th at 10:00 AM. The interview will be conducted via video call and should take approximately 45 minutes.

Please let me know which time works best for you.

Best regards,
Sarah Johnson
HR Manager, TechCorp`
    },
    {
      type: 'Job Offer',
      content: `Subject: Job Offer - Marketing Manager Position

Dear Jane,

We are pleased to offer you the position of Marketing Manager at Innovation Inc. After careful consideration, we believe you would be a great fit for our team.

The position comes with a competitive salary of $85,000 per year, full benefits package, and opportunities for professional development.

Please review the attached offer letter and let us know if you would like to accept this position. We would like to have your response by Friday, March 15th.

Congratulations, and we look forward to hearing from you soon!

Best regards,
Mike Thompson
Director of Marketing, Innovation Inc.`
    },
    {
      type: 'Recruiter Outreach',
      content: `Subject: Exciting Opportunity - Senior Developer Role

Hi Alex,

I hope this message finds you well. I came across your profile and was impressed by your experience in full-stack development.

I'm currently working with a fast-growing startup that's looking for a Senior Developer to join their team. The role offers competitive compensation, equity, and the opportunity to work on cutting-edge projects.

Would you be interested in learning more about this opportunity? I'd love to schedule a brief call to discuss the details.

Best regards,
Lisa Chen
Technical Recruiter, TalentFirst`
    }
  ];

  useEffect(() => {
    fetchTones();
  }, []);

  const fetchTones = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/tones`);
      const data = await response.json();
      setAvailableTones(data.tones);
    } catch (err) {
      console.error('Error fetching tones:', err);
    }
  };

  const handleGenerateReplies = async () => {
    if (!originalEmail.trim()) {
      setError('Please enter an email to generate replies');
      return;
    }

    setIsLoading(true);
    setError('');
    setReplies([]);

    try {
      const response = await fetch(`${BACKEND_URL}/api/generate-replies`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          original_email: originalEmail,
          context: context,
          user_name: userName
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate replies');
      }

      const data = await response.json();
      setReplies(data.replies);
      setEmailType(data.email_type);
      setShowSingleReply(false);
    } catch (err) {
      setError(`Error generating replies: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateSingleReply = async () => {
    if (!originalEmail.trim()) {
      setError('Please enter an email to generate a reply');
      return;
    }

    setIsLoading(true);
    setError('');
    setReplies([]);

    try {
      const response = await fetch(`${BACKEND_URL}/api/generate-single-reply`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          original_email: originalEmail,
          context: context,
          user_name: userName,
          tone: selectedTone
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate reply');
      }

      const data = await response.json();
      setReplies([data]);
      setEmailType(data.email_type);
      setShowSingleReply(true);
    } catch (err) {
      setError(`Error generating reply: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text, replyId) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedId(replyId);
      setTimeout(() => setCopiedId(''), 2000);
    });
  };

  const loadSampleEmail = (sample) => {
    setOriginalEmail(sample.content);
    setContext(`This is a sample ${sample.type.toLowerCase()} email.`);
    setUserName('John Doe');
  };

  const getToneColor = (tone) => {
    switch (tone) {
      case 'professional': return 'bg-blue-100 text-blue-800';
      case 'enthusiastic': return 'bg-green-100 text-green-800';
      case 'casual': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'interview_invitation': return 'bg-blue-100 text-blue-800';
      case 'job_offer': return 'bg-green-100 text-green-800';
      case 'recruiter_outreach': return 'bg-purple-100 text-purple-800';
      case 'networking': return 'bg-yellow-100 text-yellow-800';
      case 'follow_up': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatType = (type) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              AI Email Reply Assistant
            </h1>
            <p className="text-lg text-gray-600 mb-6">
              Generate professional email replies for job seekers with AI assistance
            </p>
            
            {/* Sample Emails */}
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-3">Try with sample emails:</h2>
              <div className="flex flex-wrap gap-2 justify-center">
                {sampleEmails.map((sample, index) => (
                  <button
                    key={index}
                    onClick={() => loadSampleEmail(sample)}
                    className="px-4 py-2 text-sm bg-white text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
                  >
                    {sample.type}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Input Form */}
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Name (Optional)
                </label>
                <input
                  type="text"
                  value={userName}
                  onChange={(e) => setUserName(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="John Doe"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Response Tone
                </label>
                <select
                  value={selectedTone}
                  onChange={(e) => setSelectedTone(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {availableTones.map(tone => (
                    <option key={tone.value} value={tone.value}>
                      {tone.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Original Email *
              </label>
              <textarea
                value={originalEmail}
                onChange={(e) => setOriginalEmail(e.target.value)}
                rows={8}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Paste the email you received here..."
              />
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Additional Context (Optional)
              </label>
              <textarea
                value={context}
                onChange={(e) => setContext(e.target.value)}
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Any additional context about your situation, preferences, or specific points you want to address..."
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                <p className="text-red-800">{error}</p>
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={handleGenerateReplies}
                disabled={isLoading}
                className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Generating...' : 'Generate Multiple Replies'}
              </button>
              <button
                onClick={handleGenerateSingleReply}
                disabled={isLoading}
                className="flex-1 bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Generating...' : 'Generate Single Reply'}
              </button>
            </div>
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600">Generating your professional email replies...</p>
            </div>
          )}

          {/* Results */}
          {replies.length > 0 && (
            <div className="space-y-6">
              {emailType && (
                <div className="text-center">
                  <span className={`inline-block px-4 py-2 rounded-full text-sm font-medium ${getTypeColor(emailType)}`}>
                    Email Type: {formatType(emailType)}
                  </span>
                </div>
              )}

              {replies.map((reply, index) => (
                <div key={reply.reply_id} className="bg-white rounded-xl shadow-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {showSingleReply ? 'Generated Reply' : `Reply Option ${index + 1}`}
                      </h3>
                      {!showSingleReply && (
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getToneColor(reply.tone)}`}>
                          {reply.tone.charAt(0).toUpperCase() + reply.tone.slice(1)}
                        </span>
                      )}
                    </div>
                    <button
                      onClick={() => copyToClipboard(reply.reply_content, reply.reply_id)}
                      className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
                    >
                      {copiedId === reply.reply_id ? 'Copied!' : 'Copy'}
                    </button>
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-4">
                    <pre className="whitespace-pre-wrap text-gray-800 font-sans">
                      {reply.reply_content}
                    </pre>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;