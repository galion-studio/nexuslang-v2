import React, { useState } from 'react'
import { View, StyleSheet, Dimensions } from 'react-native'
import { ChatInterface } from '../../components/chat/ChatInterface'
import { LinearGradient } from 'expo-linear-gradient'

const { height } = Dimensions.get('window')

export default function ChatScreen() {
  const [messages, setMessages] = useState([])

  const handleSendMessage = (message: string) => {
    console.log('Sending message:', message)
    // Here you would send the message to your AI API
  }

  const handleVoiceMessage = (audioBlob: Blob) => {
    console.log('Received voice message:', audioBlob)
    // Here you would process the voice message
  }

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#667eea', '#764ba2']}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <ChatInterface
            initialMessages={messages}
            onSendMessage={handleSendMessage}
            onVoiceMessage={handleVoiceMessage}
            placeholder="Ask me anything..."
            className="max-w-full"
          />
        </View>
      </LinearGradient>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    flex: 1,
    paddingTop: 50,
  },
  headerContent: {
    flex: 1,
    padding: 20,
  },
})
