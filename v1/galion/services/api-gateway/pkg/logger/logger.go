// Package logger provides structured logging utilities
package logger

import (
	"fmt"
	"log"
	"os"
	"time"
)

// Logger represents a structured logger
type Logger struct {
	debug bool
}

// New creates a new logger instance
func New(debug bool) *Logger {
	return &Logger{debug: debug}
}

// Info logs an informational message
func (l *Logger) Info(format string, v ...interface{}) {
	l.log("INFO", format, v...)
}

// Error logs an error message
func (l *Logger) Error(format string, v ...interface{}) {
	l.log("ERROR", format, v...)
}

// Debug logs a debug message (only if debug mode is enabled)
func (l *Logger) Debug(format string, v ...interface{}) {
	if l.debug {
		l.log("DEBUG", format, v...)
	}
}

// Warn logs a warning message
func (l *Logger) Warn(format string, v ...interface{}) {
	l.log("WARN", format, v...)
}

// log is the internal logging function
func (l *Logger) log(level string, format string, v ...interface{}) {
	timestamp := time.Now().Format("2006-01-02 15:04:05")
	message := fmt.Sprintf(format, v...)
	log.Printf("[%s] %s: %s", timestamp, level, message)
}

// Fatal logs a fatal error and exits the program
func (l *Logger) Fatal(format string, v ...interface{}) {
	l.log("FATAL", format, v...)
	os.Exit(1)
}

