/**
 * Tests for PersonalityEditor component
 */

import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import PersonalityEditor from '@/components/PersonalityEditor'

describe('PersonalityEditor', () => {
  const mockOnInsert = jest.fn()
  const mockOnClose = jest.fn()
  
  beforeEach(() => {
    jest.clearAllMocks()
  })
  
  it('renders personality editor with traits', () => {
    render(<PersonalityEditor onInsert={mockOnInsert} onClose={mockOnClose} />)
    
    expect(screen.getByText('Personality Editor')).toBeInTheDocument()
    expect(screen.getByText(/curiosity/i)).toBeInTheDocument()
    expect(screen.getByText(/analytical/i)).toBeInTheDocument()
    expect(screen.getByText(/creative/i)).toBeInTheDocument()
  })
  
  it('allows adjusting trait values', () => {
    render(<PersonalityEditor onInsert={mockOnInsert} onClose={mockOnClose} />)
    
    const sliders = screen.getAllByRole('slider')
    expect(sliders.length).toBeGreaterThan(0)
    
    // Adjust first slider
    fireEvent.change(sliders[0], { target: { value: '0.5' } })
  })
  
  it('calls onInsert when Insert Code button clicked', () => {
    render(<PersonalityEditor onInsert={mockOnInsert} onClose={mockOnClose} />)
    
    const insertButton = screen.getByText('Insert Code')
    fireEvent.click(insertButton)
    
    expect(mockOnInsert).toHaveBeenCalledTimes(1)
    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })
  
  it('calls onClose when Cancel button clicked', () => {
    render(<PersonalityEditor onInsert={mockOnInsert} onClose={mockOnClose} />)
    
    const cancelButton = screen.getByText('Cancel')
    fireEvent.click(cancelButton)
    
    expect(mockOnClose).toHaveBeenCalledTimes(1)
    expect(mockOnInsert).not.toHaveBeenCalled()
  })
  
  it('generates correct personality code', () => {
    render(<PersonalityEditor onInsert={mockOnInsert} onClose={mockOnClose} />)
    
    const insertButton = screen.getByText('Insert Code')
    fireEvent.click(insertButton)
    
    const generatedCode = mockOnInsert.mock.calls[0][0]
    
    expect(generatedCode).toContain('personality {')
    expect(generatedCode).toContain('curiosity:')
    expect(generatedCode).toContain('}')
  })
})

