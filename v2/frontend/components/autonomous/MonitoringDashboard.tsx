"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Server,
  Users,
  Zap,
  TrendingUp,
  RefreshCw,
  Bell,
  BellOff
} from 'lucide-react';
import { Switch } from '../ui/switch';

interface MonitoringStatus {
  active_executions: number;
  active_clients: number;
  total_alerts: number;
  uptime: number;
}

interface AlertItem {
  id: string;
  severity: string;
  title: string;
  message: string;
  timestamp: string;
  execution_id?: string;
  component: string;
}

interface PerformanceMetrics {
  average_response_time: number;
  p95_response_time: number;
  average_cpu_usage: number;
  average_memory_usage: number;
  total_agent_cost: number;
  total_agent_calls: number;
  average_active_executions: number;
}

interface ExecutionTimeline {
  execution_id: string;
  duration: number | null;
  event_count: number;
  events: Array<{
    id: string;
    type: string;
    timestamp: string;
    execution_id: string;
    data: any;
  }>;
  start_time: string | null;
  end_time: string | null;
}

export default function MonitoringDashboard() {
  const [monitoringStatus, setMonitoringStatus] = useState<MonitoringStatus | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null);
  const [selectedExecution, setSelectedExecution] = useState<string | null>(null);
  const [executionTimeline, setExecutionTimeline] = useState<ExecutionTimeline | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  const websocketRef = useRef<WebSocket | null>(null);
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize monitoring
  useEffect(() => {
    loadMonitoringData();
    connectWebSocket();

    if (autoRefresh) {
      refreshIntervalRef.current = setInterval(loadMonitoringData, 5000);
    }

    return () => {
      if (websocketRef.current) {
        websocketRef.current.close();
      }
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, [autoRefresh]);

  const loadMonitoringData = async () => {
    try {
      const [statusRes, alertsRes, perfRes] = await Promise.all([
        fetch('/api/v1/agents/monitoring/status'),
        fetch('/api/v1/agents/monitoring/alerts'),
        fetch('/api/v1/agents/monitoring/performance')
      ]);

      if (statusRes.ok) {
        const status = await statusRes.json();
        setMonitoringStatus(status);
      }

      if (alertsRes.ok) {
        const alertsData = await alertsRes.json();
        setAlerts(alertsData.alerts || []);
      }

      if (perfRes.ok) {
        const perfData = await perfRes.json();
        setPerformance(perfData);
      }

      setIsLoading(false);
    } catch (error) {
      console.error('Failed to load monitoring data:', error);
      setIsLoading(false);
    }
  };

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket(`ws://${window.location.host}/api/v1/agents/ws/monitor`);

      ws.onopen = () => {
        console.log('🔌 Connected to monitoring WebSocket');
        ws.send(JSON.stringify({
          type: 'subscribe',
          subscriptions: ['monitoring', 'alerts']
        }));
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };

      ws.onclose = () => {
        console.log('🔌 Monitoring WebSocket disconnected');
        // Auto-reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
      };

      ws.onerror = (error) => {
        console.error('Monitoring WebSocket error:', error);
      };

      websocketRef.current = ws;
    } catch (error) {
      console.error('Failed to connect monitoring WebSocket:', error);
    }
  };

  const handleWebSocketMessage = (data: any) => {
    if (data.type === 'alert') {
      // Add new alert to the list
      setAlerts(prev => [data.data, ...prev.slice(0, 9)]); // Keep last 10

      // Show notification if enabled
      if (notificationsEnabled && 'Notification' in window) {
        new Notification(`Agent Alert: ${data.data.title}`, {
          body: data.data.message,
          icon: '/favicon.ico'
        });
      }
    } else if (data.type === 'status_update') {
      // Update monitoring status
      setMonitoringStatus(data.data);
    }
  };

  const loadExecutionTimeline = async (executionId: string) => {
    try {
      const response = await fetch(`/api/v1/agents/monitoring/timeline/${executionId}`);
      if (response.ok) {
        const timeline = await response.json();
        setExecutionTimeline(timeline);
        setSelectedExecution(executionId);
      }
    } catch (error) {
      console.error('Failed to load execution timeline:', error);
    }
  };

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${mins}m`;
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-500';
      case 'error':
        return 'bg-orange-500';
      case 'warning':
        return 'bg-yellow-500';
      default:
        return 'bg-blue-500';
    }
  };

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'execution_started':
        return <Play className="h-3 w-3" />;
      case 'execution_completed':
        return <CheckCircle className="h-3 w-3" />;
      case 'execution_failed':
        return <AlertTriangle className="h-3 w-3" />;
      case 'step_started':
        return <Clock className="h-3 w-3" />;
      case 'step_completed':
        return <CheckCircle className="h-3 w-3" />;
      case 'step_failed':
        return <AlertTriangle className="h-3 w-3" />;
      default:
        return <Activity className="h-3 w-3" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="h-6 w-6 animate-spin" />
        <span className="ml-2">Loading monitoring data...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Agent Monitoring Dashboard</h1>
          <p className="text-muted-foreground">
            Real-time monitoring of the autonomous agent system
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Switch
              checked={autoRefresh}
              onCheckedChange={setAutoRefresh}
            />
            <span className="text-sm">Auto-refresh</span>
          </div>
          <div className="flex items-center gap-2">
            <Switch
              checked={notificationsEnabled}
              onCheckedChange={setNotificationsEnabled}
            />
            <Bell className="h-4 w-4" />
          </div>
          <Button onClick={loadMonitoringData} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Executions</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{monitoringStatus?.active_executions || 0}</div>
            <p className="text-xs text-muted-foreground">
              Tasks currently running
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Connected Clients</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{monitoringStatus?.active_clients || 0}</div>
            <p className="text-xs text-muted-foreground">
              WebSocket connections
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {alerts.filter(a => !a.resolved).length}
            </div>
            <p className="text-xs text-muted-foreground">
              Unresolved issues
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Uptime</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {monitoringStatus ? formatUptime(monitoringStatus.uptime) : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground">
              Since last restart
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Metrics */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Performance Metrics
            </CardTitle>
            <CardDescription>
              Real-time performance indicators
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {performance ? (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm font-medium">Avg Response Time</div>
                    <div className="text-lg font-bold">
                      {performance.average_response_time?.toFixed(2) || 'N/A'}s
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium">95th Percentile</div>
                    <div className="text-lg font-bold">
                      {performance.p95_response_time?.toFixed(2) || 'N/A'}s
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium">CPU Usage</div>
                    <div className="text-lg font-bold">
                      {performance.average_cpu_usage?.toFixed(1) || 'N/A'}%
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium">Memory Usage</div>
                    <div className="text-lg font-bold">
                      {performance.average_memory_usage?.toFixed(1) || 'N/A'}%
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Agent Calls</span>
                    <span>{performance.total_agent_calls || 0}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Total Cost</span>
                    <span>${performance.total_agent_cost?.toFixed(4) || '0.0000'}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Active Tasks</span>
                    <span>{Math.round(performance.average_active_executions || 0)}</span>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center text-muted-foreground py-8">
                No performance data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Alerts */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Recent Alerts
            </CardTitle>
            <CardDescription>
              Latest system alerts and notifications
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {alerts.length > 0 ? (
                alerts.slice(0, 10).map((alert) => (
                  <Alert key={alert.id} className="border-l-4" style={{
                    borderLeftColor: alert.severity === 'critical' ? '#ef4444' :
                                   alert.severity === 'error' ? '#f97316' :
                                   alert.severity === 'warning' ? '#eab308' : '#3b82f6'
                  }}>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge className={getSeverityColor(alert.severity)}>
                            {alert.severity}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {new Date(alert.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="font-medium text-sm">{alert.title}</div>
                        <AlertDescription className="text-xs mt-1">
                          {alert.message}
                        </AlertDescription>
                        {alert.execution_id && (
                          <Button
                            variant="link"
                            size="sm"
                            className="p-0 h-auto mt-1"
                            onClick={() => loadExecutionTimeline(alert.execution_id!)}
                          >
                            View Execution
                          </Button>
                        )}
                      </div>
                    </div>
                  </Alert>
                ))
              ) : (
                <div className="text-center text-muted-foreground py-8">
                  No recent alerts
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Execution Timeline */}
      {executionTimeline && (
        <Card>
          <CardHeader>
            <CardTitle>Execution Timeline: {selectedExecution}</CardTitle>
            <CardDescription>
              Duration: {formatDuration(executionTimeline.duration)} |
              Events: {executionTimeline.event_count}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {executionTimeline.events.map((event, index) => (
                <div key={event.id} className="flex items-start gap-3 p-2 rounded border">
                  <div className="mt-0.5">
                    {getEventIcon(event.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">
                        {event.type.replace('_', ' ')}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    {event.data && Object.keys(event.data).length > 0 && (
                      <div className="text-xs text-muted-foreground mt-1">
                        {JSON.stringify(event.data).slice(0, 100)}
                        {JSON.stringify(event.data).length > 100 && '...'}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Request notification permission */}
      {typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'default' && (
        <Alert>
          <Bell className="h-4 w-4" />
          <AlertDescription>
            Enable notifications to receive real-time alerts about agent executions and system issues.
            <Button
              variant="link"
              className="p-0 ml-2"
              onClick={() => Notification.requestPermission()}
            >
              Enable Notifications
            </Button>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
