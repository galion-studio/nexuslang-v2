"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { AlertCircle, Play, Square, CheckCircle, XCircle, Clock, Zap } from 'lucide-react';
import { Alert, AlertDescription } from '../ui/alert';

interface TaskExecution {
  task_id: string;
  status: string;
  progress: number;
  current_step?: number;
  total_steps?: number;
  started_at?: string;
  completed_at?: string;
  result?: any;
  error?: string;
  steps?: Array<{
    id: string;
    description: string;
    status: string;
    result?: any;
    error?: string;
  }>;
}

interface TaskExecutorProps {
  onTaskComplete?: (result: TaskExecution) => void;
  className?: string;
}

export default function TaskExecutor({ onTaskComplete, className }: TaskExecutorProps) {
  const [prompt, setPrompt] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [currentTask, setCurrentTask] = useState<TaskExecution | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [nlpAnalysis, setNlpAnalysis] = useState<any>(null);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const websocketRef = useRef<WebSocket | null>(null);

  // Initialize WebSocket connection for real-time updates
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(`ws://${window.location.host}/api/v1/agents/ws/monitor`);

        ws.onopen = () => {
          console.log('🔌 Connected to agent monitoring');
          ws.send(JSON.stringify({
            type: 'subscribe',
            subscriptions: ['tasks', 'approvals', 'monitoring']
          }));
        };

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        };

        ws.onclose = () => {
          console.log('🔌 Disconnected from agent monitoring');
          // Auto-reconnect after 5 seconds
          setTimeout(connectWebSocket, 5000);
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };

        websocketRef.current = ws;
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
      }
    };

    connectWebSocket();

    return () => {
      if (websocketRef.current) {
        websocketRef.current.close();
      }
    };
  }, []);

  const handleWebSocketMessage = (data: any) => {
    if (data.type === 'task_started' && currentTask?.task_id === data.task_id) {
      setCurrentTask(prev => prev ? {
        ...prev,
        status: 'running',
        started_at: data.timestamp
      } : null);
    } else if (data.type === 'task_cancelled' && currentTask?.task_id === data.task_id) {
      setCurrentTask(prev => prev ? {
        ...prev,
        status: 'cancelled'
      } : null);
      setIsExecuting(false);
    }
  };

  const analyzeTask = async () => {
    if (!prompt.trim()) return;

    try {
      const response = await fetch('/api/v1/agents/nlp/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: prompt,
          context: { include_plan: true }
        }),
      });

      if (!response.ok) throw new Error('Analysis failed');

      const analysis = await response.json();
      setNlpAnalysis(analysis);
      setShowAnalysis(true);
    } catch (error) {
      console.error('Analysis error:', error);
      setError('Failed to analyze task');
    }
  };

  const executeTask = async () => {
    if (!prompt.trim()) return;

    setIsExecuting(true);
    setError(null);
    setCurrentTask(null);

    try {
      const response = await fetch('/api/v1/agents/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt,
          context: {
            source: 'frontend',
            timestamp: new Date().toISOString()
          },
          require_approval: false, // Could be made configurable
          priority: 'normal',
          tags: ['frontend', 'user-initiated']
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Execution failed');
      }

      const result = await response.json();
      setCurrentTask({
        task_id: result.task_id,
        status: 'running',
        progress: 0
      });

      // Start polling for status updates
      pollTaskStatus(result.task_id);

    } catch (error: any) {
      console.error('Execution error:', error);
      setError(error.message || 'Failed to execute task');
      setIsExecuting(false);
    }
  };

  const pollTaskStatus = async (taskId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/v1/agents/status/${taskId}`);

        if (!response.ok) {
          if (response.status === 404) {
            clearInterval(pollInterval);
            setError('Task not found');
            setIsExecuting(false);
            return;
          }
          throw new Error('Status check failed');
        }

        const status = await response.json();
        setCurrentTask(status);

        if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
          clearInterval(pollInterval);
          setIsExecuting(false);

          if (onTaskComplete) {
            onTaskComplete(status);
          }
        }
      } catch (error) {
        console.error('Status poll error:', error);
        clearInterval(pollInterval);
        setIsExecuting(false);
        setError('Failed to check task status');
      }
    }, 2000); // Poll every 2 seconds

    // Stop polling after 10 minutes
    setTimeout(() => {
      clearInterval(pollInterval);
      if (isExecuting) {
        setIsExecuting(false);
        setError('Task execution timed out');
      }
    }, 600000);
  };

  const cancelTask = async () => {
    if (!currentTask?.task_id) return;

    try {
      const response = await fetch(`/api/v1/agents/cancel/${currentTask.task_id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Cancellation failed');
      }

      setIsExecuting(false);
      setCurrentTask(prev => prev ? { ...prev, status: 'cancelled' } : null);
    } catch (error) {
      console.error('Cancellation error:', error);
      setError('Failed to cancel task');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <Clock className="h-4 w-4 animate-spin text-blue-500" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'cancelled':
        return <Square className="h-4 w-4 text-gray-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-blue-500';
      case 'completed':
        return 'bg-green-500';
      case 'failed':
        return 'bg-red-500';
      case 'cancelled':
        return 'bg-gray-500';
      default:
        return 'bg-yellow-500';
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Autonomous Task Executor
          </CardTitle>
          <CardDescription>
            Describe your task in natural language and watch it execute autonomously
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Textarea
              placeholder="e.g., 'Build a complete user authentication system with login, registration, password reset, and email verification'"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="min-h-[120px]"
              disabled={isExecuting}
            />
            <div className="flex gap-2">
              <Button
                onClick={analyzeTask}
                variant="outline"
                disabled={!prompt.trim() || isExecuting}
              >
                Analyze Task
              </Button>
              <Button
                onClick={executeTask}
                disabled={!prompt.trim() || isExecuting}
                className="flex-1"
              >
                {isExecuting ? (
                  <>
                    <Clock className="h-4 w-4 mr-2 animate-spin" />
                    Executing...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Execute Task
                  </>
                )}
              </Button>
            </div>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {nlpAnalysis && showAnalysis && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">NLP Analysis</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex gap-2 flex-wrap">
                  <Badge variant="outline">Intent: {nlpAnalysis.intent}</Badge>
                  <Badge variant="outline">Complexity: {nlpAnalysis.complexity}</Badge>
                  <Badge variant="outline">Risk: {nlpAnalysis.risk_level}</Badge>
                  <Badge variant="outline">Confidence: {Math.round(nlpAnalysis.confidence * 100)}%</Badge>
                </div>
                {nlpAnalysis.key_phrases.length > 0 && (
                  <div>
                    <span className="text-sm font-medium">Key Phrases:</span>
                    <div className="flex gap-1 flex-wrap mt-1">
                      {nlpAnalysis.key_phrases.slice(0, 5).map((phrase: string, i: number) => (
                        <Badge key={i} variant="secondary" className="text-xs">{phrase}</Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {currentTask && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  {getStatusIcon(currentTask.status)}
                  Task Execution
                  <Badge className={getStatusColor(currentTask.status)}>
                    {currentTask.status}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>{Math.round(currentTask.progress)}%</span>
                  </div>
                  <Progress value={currentTask.progress} className="w-full" />
                </div>

                {currentTask.current_step !== undefined && currentTask.total_steps && (
                  <div className="text-sm text-muted-foreground">
                    Step {currentTask.current_step} of {currentTask.total_steps}
                  </div>
                )}

                {currentTask.steps && currentTask.steps.length > 0 && (
                  <div className="space-y-2">
                    <div className="text-sm font-medium">Execution Steps:</div>
                    <div className="space-y-1 max-h-32 overflow-y-auto">
                      {currentTask.steps.map((step, index) => (
                        <div key={step.id} className="flex items-center gap-2 text-xs">
                          {getStatusIcon(step.status)}
                          <span className="truncate">{step.description}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {currentTask.status === 'running' && (
                  <Button
                    onClick={cancelTask}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    <Square className="h-4 w-4 mr-2" />
                    Cancel Execution
                  </Button>
                )}

                {currentTask.result && (
                  <div className="mt-4 p-3 bg-green-50 rounded-md">
                    <div className="text-sm font-medium text-green-800">Task Completed Successfully</div>
                    <div className="text-xs text-green-600 mt-1">
                      Result: {JSON.stringify(currentTask.result).slice(0, 100)}...
                    </div>
                  </div>
                )}

                {currentTask.error && (
                  <div className="mt-4 p-3 bg-red-50 rounded-md">
                    <div className="text-sm font-medium text-red-800">Task Failed</div>
                    <div className="text-xs text-red-600 mt-1">{currentTask.error}</div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
