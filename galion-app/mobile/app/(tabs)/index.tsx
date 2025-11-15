import React, { useState, useEffect } from 'react'
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Dimensions,
  Alert,
} from 'react-native'
import { Audio } from 'expo-av'
import { VoiceAssistant } from '../../components/voice/VoiceAssistant'
import { LinearGradient } from 'expo-linear-gradient'

const { width, height } = Dimensions.get('window')

export default function VoiceScreen() {
  const [isRecording, setIsRecording] = useState(false)
  const [recording, setRecording] = useState<Audio.Recording | null>(null)
  const [lastTranscription, setLastTranscription] = useState('')
  const [aiResponse, setAiResponse] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)

  useEffect(() => {
    // Request audio permissions
    const requestPermissions = async () => {
      const { status } = await Audio.requestPermissionsAsync()
      if (status !== 'granted') {
        Alert.alert(
          'Permission Required',
          'Audio recording permission is required for voice features.'
        )
      }
    }

    requestPermissions()

    // Set audio mode for recording
    Audio.setAudioModeAsync({
      allowsRecordingIOS: true,
      interruptionModeIOS: Audio.INTERRUPTION_MODE_IOS_DO_NOT_MIX,
      playsInSilentModeIOS: true,
      shouldDuckAndroid: true,
      interruptionModeAndroid: Audio.INTERRUPTION_MODE_ANDROID_DO_NOT_MIX,
      playThroughEarpieceAndroid: false,
    })
  }, [])

  const startRecording = async () => {
    try {
      if (recording) {
        await recording.stopAndUnloadAsync()
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        interruptionModeIOS: Audio.INTERRUPTION_MODE_IOS_DO_NOT_MIX,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: true,
        interruptionModeAndroid: Audio.INTERRUPTION_MODE_ANDROID_DO_NOT_MIX,
        playThroughEarpieceAndroid: false,
      })

      const newRecording = new Audio.Recording()
      await newRecording.prepareToRecordAsync(Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY)

      setRecording(newRecording)
      await newRecording.startAsync()
      setIsRecording(true)
    } catch (error) {
      console.error('Failed to start recording:', error)
      Alert.alert('Error', 'Failed to start recording')
    }
  }

  const stopRecording = async () => {
    try {
      if (!recording) return

      setIsRecording(false)
      setIsProcessing(true)

      await recording.stopAndUnloadAsync()
      const uri = recording.getURI()

      if (uri) {
        // Here you would send the audio file to your speech-to-text API
        // For now, we'll simulate the process
        setTimeout(() => {
          const mockTranscription = "Hello, I need help with my project."
          setLastTranscription(mockTranscription)

          // Simulate AI response
          setTimeout(() => {
            const mockResponse = "I'd be happy to help you with your project! What specific aspect would you like assistance with?"
            setAiResponse(mockResponse)
            setIsProcessing(false)

            // Auto-play the response (if TTS is enabled)
            playAIResponse(mockResponse)
          }, 1500)
        }, 2000)
      }
    } catch (error) {
      console.error('Failed to stop recording:', error)
      setIsProcessing(false)
      Alert.alert('Error', 'Failed to process recording')
    }
  }

  const playAIResponse = async (text: string) => {
    // In a real implementation, you would use Expo Speech or a TTS API
    console.log('Playing AI response:', text)
    // For now, we'll just log it
  }

  const handleVoiceCommand = (command: string) => {
    setLastTranscription(command)
    setIsProcessing(true)

    // Simulate AI processing
    setTimeout(() => {
      const response = generateAIResponse(command)
      setAiResponse(response)
      setIsProcessing(false)
      playAIResponse(response)
    }, 1000 + Math.random() * 2000)
  }

  const generateAIResponse = (command: string): string => {
    // Simple response generation - in real app, this would call your AI API
    const responses = [
      `I understand you want to "${command}". Let me help you with that.`,
      `That's an interesting request about ${command}. Here's what I can do:`,
      `Great! I'd be happy to assist you with ${command}.`,
      `Perfect! Let me help you with ${command}. What would you like to know?`,
      `I see you're asking about ${command}. Let me provide you with detailed information.`
    ]

    return responses[Math.floor(Math.random() * responses.length)]
  }

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#667eea', '#764ba2']}
        style={styles.header}
      >
        <Text style={styles.headerTitle}>Galion Voice AI</Text>
        <Text style={styles.headerSubtitle}>
          Your AI assistant, now in your pocket
        </Text>
      </LinearGradient>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Voice Assistant Component */}
        <View style={styles.voiceSection}>
          <VoiceAssistant
            onVoiceCommand={handleVoiceCommand}
            onVoiceResponse={(response) => {
              setAiResponse(response)
              playAIResponse(response)
            }}
          />
        </View>

        {/* Mobile-specific controls */}
        <View style={styles.mobileControls}>
          <TouchableOpacity
            style={[
              styles.recordButton,
              isRecording && styles.recordingButton,
              isProcessing && styles.processingButton
            ]}
            onPress={isRecording ? stopRecording : startRecording}
            disabled={isProcessing}
          >
            <View style={[
              styles.recordButtonInner,
              isRecording && styles.recordingInner
            ]}>
              {isProcessing ? (
                <Text style={styles.buttonText}>Processing...</Text>
              ) : isRecording ? (
                <Text style={styles.buttonText}>Stop Recording</Text>
              ) : (
                <Text style={styles.buttonText}>Start Voice Chat</Text>
              )}
            </View>
          </TouchableOpacity>

          {isRecording && (
            <View style={styles.recordingIndicator}>
              <View style={styles.pulseDot} />
              <Text style={styles.recordingText}>Recording...</Text>
            </View>
          )}

          {lastTranscription && (
            <View style={styles.transcriptionCard}>
              <Text style={styles.transcriptionLabel}>You said:</Text>
              <Text style={styles.transcriptionText}>{lastTranscription}</Text>
            </View>
          )}

          {aiResponse && (
            <View style={styles.responseCard}>
              <Text style={styles.responseLabel}>AI Response:</Text>
              <Text style={styles.responseText}>{aiResponse}</Text>
            </View>
          )}
        </View>

        {/* Quick Actions */}
        <View style={styles.quickActions}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionGrid}>
            {[
              { icon: '💬', label: 'Chat', desc: 'Text conversation' },
              { icon: '🎨', label: 'Create', desc: 'Generate content' },
              { icon: '💻', label: 'Code', desc: 'Programming help' },
              { icon: '📊', label: 'Analytics', desc: 'Usage insights' },
              { icon: '⚙️', label: 'Settings', desc: 'Voice preferences' },
              { icon: '📚', label: 'Learn', desc: 'AI knowledge' }
            ].map((action, index) => (
              <TouchableOpacity key={index} style={styles.actionCard}>
                <Text style={styles.actionIcon}>{action.icon}</Text>
                <Text style={styles.actionLabel}>{action.label}</Text>
                <Text style={styles.actionDesc}>{action.desc}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Voice Tips */}
        <View style={styles.tipsSection}>
          <Text style={styles.sectionTitle}>Voice Tips</Text>
          <View style={styles.tipsList}>
            <Text style={styles.tip}>• Speak clearly and at a natural pace</Text>
            <Text style={styles.tip}>• Use full sentences for better understanding</Text>
            <Text style={styles.tip}>• The AI remembers your conversation context</Text>
            <Text style={styles.tip}>• Try commands like "Show my dashboard" or "Help me code"</Text>
            <Text style={styles.tip}>• Voice responses can be customized in settings</Text>
          </View>
        </View>
      </ScrollView>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    paddingTop: 60,
    paddingBottom: 30,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  headerSubtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.9)',
    textAlign: 'center',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  voiceSection: {
    marginBottom: 20,
  },
  mobileControls: {
    marginBottom: 30,
  },
  recordButton: {
    backgroundColor: '#3b82f6',
    borderRadius: 25,
    padding: 4,
    shadowColor: '#3b82f6',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  recordingButton: {
    backgroundColor: '#ef4444',
    shadowColor: '#ef4444',
  },
  processingButton: {
    backgroundColor: '#f59e0b',
    shadowColor: '#f59e0b',
  },
  recordButtonInner: {
    paddingVertical: 15,
    paddingHorizontal: 30,
    alignItems: 'center',
    justifyContent: 'center',
  },
  recordingInner: {
    paddingVertical: 12,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  recordingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 15,
    paddingVertical: 8,
    paddingHorizontal: 16,
    backgroundColor: '#fef2f2',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#fecaca',
  },
  pulseDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#ef4444',
    marginRight: 8,
    shadowColor: '#ef4444',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.8,
    shadowRadius: 4,
    elevation: 4,
  },
  recordingText: {
    color: '#dc2626',
    fontSize: 14,
    fontWeight: '500',
  },
  transcriptionCard: {
    marginTop: 20,
    padding: 16,
    backgroundColor: 'white',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  transcriptionLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  transcriptionText: {
    fontSize: 16,
    color: '#1f2937',
    lineHeight: 24,
  },
  responseCard: {
    marginTop: 16,
    padding: 16,
    backgroundColor: '#f0f9ff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#bae6fd',
  },
  responseLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#0c4a6e',
    marginBottom: 8,
  },
  responseText: {
    fontSize: 16,
    color: '#0c4a6e',
    lineHeight: 24,
  },
  quickActions: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 16,
  },
  actionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionCard: {
    width: width * 0.28,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e5e7eb',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  actionIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  actionLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 4,
    textAlign: 'center',
  },
  actionDesc: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 16,
  },
  tipsSection: {
    marginBottom: 30,
  },
  tipsList: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  tip: {
    fontSize: 14,
    color: '#4b5563',
    marginBottom: 8,
    lineHeight: 20,
  },
})
