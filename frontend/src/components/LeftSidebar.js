import React, { useState, useRef, useEffect } from 'react';
import { useAppTheme } from '../App';
import { useUserData } from '../contexts/UserDataContext';

// Clipboard utility function with fallback
const copyToClipboardWithFallback = async (text) => {
  try {
    // Try modern Clipboard API first
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return;
    }
  } catch (error) {
    console.warn('Clipboard API failed, using fallback method:', error);
  }

  // Fallback method: Create temporary textarea element
  try {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    const result = document.execCommand('copy');
    document.body.removeChild(textArea);
    
    if (!result) {
      throw new Error('execCommand copy failed');
    }
  } catch (fallbackError) {
    console.error('All clipboard methods failed:', fallbackError);
    // Show user a manual copy option
    const userPrompt = prompt('Copy this URL manually:', text);
    if (userPrompt !== null) {
      return; // User interaction completed
    }
    throw new Error('Failed to copy to clipboard');
  }
};
import { 
  ChevronLeft, 
  ChevronRight, 
  Heart, 
  Calendar, 
  Users, 
  Image, 
  Settings, 
  LogOut,
  Edit3,
  Mail,
  MessageCircle,
  Gift,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Star,
  Plus,
  Save,
  MessageSquare,
  Share,
  QrCode,
  Link,
  Wand2,
  Eye,
  EyeOff,
  Download,
  Palette,
  Clock,
  MapPin,
  Phone,
  Copy,
  CheckCircle,
  X
} from 'lucide-react';

const LeftSidebar = () => {
  const { themes, currentTheme } = useAppTheme();
  const theme = themes[currentTheme];
  const { 
    leftSidebarOpen, 
    setLeftSidebarOpen, 
    logout, 
    userInfo,
    isAuthenticated,
    weddingData,
    saveWeddingData 
  } = useUserData();

  const [activeSection, setActiveSection] = useState('info');
  const [infoExpanded, setInfoExpanded] = useState(true);
  const [activeForm, setActiveForm] = useState(null);
  const modalRef = useRef(null);
  const [showNotification, setShowNotification] = useState(false);
  const [isHovering, setIsHovering] = useState(false);
  const sidebarRef = useRef(null);

  const editSections = [
    { id: 'home', label: 'Home', icon: Heart, description: 'Edit couple names, date, venue' },
    { id: 'story', label: 'Our Story', icon: Heart, description: 'Timeline and love story' },
    { id: 'rsvp', label: 'RSVP', icon: Mail, description: 'RSVP form settings' },
    { id: 'schedule', label: 'Schedule', icon: Calendar, description: 'Wedding day timeline' },
    { id: 'gallery', label: 'Gallery', icon: Image, description: 'Photo gallery' },
    { id: 'party', label: 'Wedding Party', icon: Users, description: 'Bridal and groom party' },
    { id: 'registry', label: 'Registry', icon: Gift, description: 'Gift registry links' },
    { id: 'guestbook', label: 'Guest Book', icon: MessageCircle, description: 'Guest messages' },
    { id: 'faq', label: 'FAQ', icon: HelpCircle, description: 'Frequently asked questions' },
    { id: 'theme', label: 'Theme', icon: Settings, description: 'Classic, Modern, or Boho' }
  ];

  // Main sidebar sections - reorganized as requested
  const sidebarSections = [
    { id: 'info', label: 'Edit the Info', icon: Edit3, expandable: true, color: '#6366F1' },
    { id: 'whatsapp', label: 'Share via WhatsApp', icon: MessageSquare, color: '#25D366' },
    { id: 'gmail', label: 'Share via Gmail', icon: Mail, color: '#EA4335' },
    { id: 'qrcode', label: 'Get QR Code', icon: QrCode, color: '#6366F1' },
    { id: 'url', label: 'Get Shareable URL', icon: Link, color: '#3B82F6' },
    { id: 'ai', label: 'Generate Design with AI', icon: Wand2, color: '#8B5CF6' }
  ];

  // Handle click outside modal to auto-save immediately
  useEffect(() => {
    const handleClickOutside = (event) => {
      // Check if click is on a form input, button, or other interactive element
      const isInteractiveElement = event.target.tagName === 'INPUT' || 
                                 event.target.tagName === 'BUTTON' || 
                                 event.target.tagName === 'SELECT' || 
                                 event.target.tagName === 'TEXTAREA' ||
                                 event.target.closest('button') ||
                                 event.target.closest('input') ||
                                 event.target.closest('select') ||
                                 event.target.closest('textarea');
      
      // Only close modal if clicked outside and not on interactive elements
      if (modalRef.current && !modalRef.current.contains(event.target) && !isInteractiveElement) {
        if (activeForm) {
          // Immediate auto-save and close (no delay)
          setShowNotification(true);
          setActiveForm(null);
          setTimeout(() => {
            setShowNotification(false);
          }, 1500);
        }
      }
      
      // Handle sidebar click outside when expanded by hover
      if (sidebarRef.current && !sidebarRef.current.contains(event.target) && !leftSidebarOpen && isHovering) {
        setIsHovering(false);
      }
    };

    if (activeForm) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscapeKey);
    }
    
    // Always listen for clicks outside sidebar when it's hovered open
    if (!leftSidebarOpen && isHovering) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, [activeForm, leftSidebarOpen, isHovering]);

  const handleEscapeKey = (event) => {
    if (event.key === 'Escape' && activeForm) {
      setActiveForm(null);
    }
  };

  const handleSectionClick = (sectionId) => {
    switch (sectionId) {
      case 'whatsapp':
      case 'gmail':
        handlePremiumFeature(sectionId);
        break;
      case 'qrcode':
        setActiveForm('qrcode-generator');
        break;
      case 'url':
        handlePremiumFeature(sectionId);
        break;
      case 'ai':
        setActiveForm('ai-design');
        break;
      default:
        break;
    }
  };

  const handlePremiumFeature = (featureId) => {
    // Get the system-generated custom URL from wedding data
    const shareableUrl = weddingData.custom_url 
      ? `${window.location.origin}/${weddingData.custom_url}`
      : `${window.location.origin}/wedding/${userInfo.userId}`;
    
    console.log('Shareable URL:', shareableUrl, 'Custom URL:', weddingData.custom_url);
    
    switch (featureId) {
      case 'whatsapp':
        const whatsappText = `Check out our wedding card! 💒✨ ${weddingData.couple_name_1} & ${weddingData.couple_name_2} are getting married on ${weddingData.wedding_date}! ${shareableUrl}`;
        
        // Detect if user is on mobile or desktop
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        if (isMobile) {
          // Mobile: Open WhatsApp app directly with pre-filled message
          const whatsappAppUrl = `whatsapp://send?text=${encodeURIComponent(whatsappText)}`;
          window.open(whatsappAppUrl, '_blank');
        } else {
          // Desktop: Open WhatsApp Web with pre-filled message - allows selecting multiple contacts
          const whatsappWebUrl = `https://web.whatsapp.com/send?text=${encodeURIComponent(whatsappText)}`;
          window.open(whatsappWebUrl, '_blank');
        }
        break;
      
      case 'gmail':
        const subject = `${weddingData.couple_name_1} & ${weddingData.couple_name_2}'s Wedding Invitation`;
        const body = `You're invited to our wedding! 💕\n\nView our beautiful wedding card: ${shareableUrl}\n\nDate: ${weddingData.wedding_date}\nVenue: ${weddingData.venue_location}\n\nWe can't wait to celebrate with you!\n\nWith love,\n${weddingData.couple_name_1} & ${weddingData.couple_name_2}`;
        const gmailUrl = `https://mail.google.com/mail/?view=cm&fs=1&to=&su=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
        window.open(gmailUrl, '_blank');
        break;
      
      case 'qrcode':
        // Generate QR code using QR Server API
        const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(shareableUrl)}`;
        const newWindow = window.open('', '_blank');
        newWindow.document.write(`
          <html>
            <head><title>QR Code - Wedding Card</title></head>
            <body style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; font-family: Arial, sans-serif; background: linear-gradient(135deg, #f8f6f0, #ffffff);">
              <h2 style="color: #333; margin-bottom: 20px;">Wedding Card QR Code</h2>
              <img src="${qrUrl}" alt="QR Code" style="border: 4px solid #d4af37; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);" />
              <p style="color: #666; margin-top: 20px; text-align: center; max-width: 300px;">Scan this QR code to view the wedding card</p>
              <button onclick="window.print()" style="margin-top: 20px; padding: 10px 20px; background: linear-gradient(135deg, #d4af37, #f4e4a6); border: none; border-radius: 8px; color: white; font-weight: bold; cursor: pointer;">Print QR Code</button>
            </body>
          </html>
        `);
        break;
      
      case 'url':
        copyToClipboardWithFallback(shareableUrl).then(() => {
          setShowNotification(true);
          setTimeout(() => setShowNotification(false), 2000);
        }).catch((error) => {
          console.error('Failed to copy URL:', error);
          setShowNotification(true);
          setTimeout(() => setShowNotification(false), 2000);
        });
        break;
      
      case 'ai':
        // AI Design Generator Modal
        setActiveForm('ai-design');
        break;
      
      default:
        break;
    }
  };

  // Don't render anything if not authenticated
  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      {/* Notification Toast */}
      {showNotification && (
        <div className="fixed top-4 right-4 z-[60] bg-green-500 text-white px-6 py-3 rounded-xl shadow-2xl flex items-center gap-2 animate-slide-in-right">
          <CheckCircle className="w-5 h-5" />
          <span>
            {activeForm === 'url' ? 'URL copied to clipboard!' : 'Changes saved automatically!'}
          </span>
        </div>
      )}

      {/* Left Sidebar */}
      <div 
        ref={sidebarRef}
        className={`fixed left-0 top-0 h-full backdrop-blur-xl border-r border-white/30 shadow-2xl transition-all duration-500 ease-in-out z-40 ${
          leftSidebarOpen || (!leftSidebarOpen && isHovering) ? 'w-80 md:w-80' : 'w-16 md:w-20'
        }`}
        style={{ 
          background: window.innerWidth <= 768 
            ? `linear-gradient(135deg, ${theme.background}70, ${theme.secondary}60)` // More translucent on mobile
            : `linear-gradient(135deg, ${theme.background}f0, ${theme.secondary}e0)`, // Less translucent on desktop
          borderColor: `${theme.accent}20`
        }}
        onMouseEnter={() => {
          // Only enable hover on desktop
          if (!leftSidebarOpen && window.innerWidth > 768) {
            setIsHovering(true);
          }
        }}
        onMouseLeave={() => {
          // Don't auto-close on mouse leave - user requested it stays open
          // It will only close when clicking outside
        }}
        onClick={(e) => {
          // On mobile, clicking the sidebar when collapsed should open it
          if (window.innerWidth <= 768 && !leftSidebarOpen && e.target === e.currentTarget) {
            setLeftSidebarOpen(true);
          }
        }}
      >
        {/* Toggle Button */}
        <button
          onClick={() => setLeftSidebarOpen(!leftSidebarOpen)}
          className="absolute -right-4 top-20 w-8 h-16 bg-white border border-gray-200 rounded-r-xl flex items-center justify-center shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-110 z-50"
          style={{ 
            background: theme.gradientAccent,
            borderColor: `${theme.accent}30`
          }}
        >
          {leftSidebarOpen ? (
            <ChevronLeft className="w-4 h-4" style={{ color: theme.primary }} />
          ) : (
            <ChevronRight className="w-4 h-4" style={{ color: theme.primary }} />
          )}
        </button>

        {/* Sidebar Content */}
        <div className="h-full flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-white/20">
            <div className="flex items-center gap-3">
              <div 
                className="w-10 h-10 rounded-full flex items-center justify-center animate-pulse"
                style={{ background: theme.gradientAccent }}
              >
                <Edit3 className="w-5 h-5" style={{ color: theme.primary }} />
              </div>
              {leftSidebarOpen || (!leftSidebarOpen && isHovering) && (
                <div>
                  <h2 
                    className="text-lg font-semibold"
                    style={{ 
                      fontFamily: theme.fontPrimary,
                      color: theme.primary 
                    }}
                  >
                    Wedding Editor
                  </h2>
                  <p className="text-sm opacity-70" style={{ color: theme.textLight }}>
                    Welcome, {userInfo?.username}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Navigation */}
          <div className="flex-1 p-4 overflow-y-auto">
            <nav className="space-y-2">
              {sidebarSections.map((section) => {
                const Icon = section.icon;
                const isActive = activeSection === section.id;
                const isInfoSection = section.id === 'info';
                
                return (
                  <div key={section.id}>
                    <button
                      onClick={() => {
                        setActiveSection(section.id);
                        if (isInfoSection) {
                          setInfoExpanded(!infoExpanded);
                        } else {
                          // Handle premium features and custom actions
                          handleSectionClick(section.id);
                        }
                      }}
                      className={`w-full flex items-center justify-between p-3 rounded-xl transition-all duration-300 hover:scale-105 group ${
                        isActive ? 'shadow-lg' : 'hover:shadow-md'
                      }`}
                      style={{
                        background: isActive 
                          ? theme.gradientAccent 
                          : 'rgba(255,255,255,0.1)',
                        color: isActive 
                          ? theme.primary 
                          : theme.text
                      }}
                      title={!(leftSidebarOpen || isHovering) ? section.label : ''}
                    >
                      <div className="flex items-center gap-3">
                        <Icon 
                          className="w-5 h-5" 
                          style={{ color: section.color || theme.text }}
                        />
                        {(leftSidebarOpen || (!leftSidebarOpen && isHovering)) && (
                          <span className="font-medium">{section.label}</span>
                        )}
                      </div>
                      {(leftSidebarOpen || (!leftSidebarOpen && isHovering)) && isInfoSection && (
                        infoExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                      )}
                    </button>
                    
                    {/* Info Section Dropdown */}
                    {isInfoSection && infoExpanded && (leftSidebarOpen || (!leftSidebarOpen && isHovering)) && (
                      <div className="mt-2 ml-4 space-y-1">
                        {editSections.map((editSection) => {
                          const EditIcon = editSection.icon;
                          return (
                            <button
                              key={editSection.id}
                              onClick={() => setActiveForm(editSection.id)}
                              className="w-full flex items-center gap-3 p-3 rounded-lg transition-all duration-200 hover:bg-white/10 group animate-fade-in"
                              style={{ color: theme.textLight }}
                            >
                              <EditIcon className="w-4 h-4" />
                              <div className="text-left">
                                <div className="text-sm font-medium group-hover:font-semibold transition-all duration-200">
                                  {editSection.label}
                                </div>
                                <div className="text-xs opacity-70">
                                  {editSection.description}
                                </div>
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}
            </nav>

            {/* Section removed - premium features now integrated into main navigation */}
          </div>

          {/* Footer - Logout */}
          <div className="p-4 border-t border-white/20">
            <button
              onClick={logout}
              className="w-full flex items-center gap-3 p-3 rounded-xl transition-all duration-300 hover:bg-red-500/10 hover:scale-105"
              style={{ color: theme.textLight }}
              title={!(leftSidebarOpen || isHovering) ? 'Logout' : ''}
            >
              <LogOut className="w-5 h-5" />
              {(leftSidebarOpen || (!leftSidebarOpen && isHovering)) && <span>Logout</span>}
            </button>
          </div>
        </div>
      </div>

      {/* Form Popups */}
      {activeForm && (
        <FormPopup
          sectionId={activeForm}
          onClose={() => setActiveForm(null)}
          theme={theme}
          modalRef={modalRef}
        />
      )}

      {/* Main Content Pusher - Adds margin when sidebar is open */}
      <div 
        className={`transition-all duration-500 ease-in-out ${
          leftSidebarOpen ? 'ml-80' : 'ml-20'
        }`}
        style={{ minHeight: '100vh' }}
      />
    </>
  );
};

// Enhanced Form Popup Component with Auto-save and Premium Features
const FormPopup = ({ sectionId, onClose, theme, modalRef }) => {
  const { weddingData, saveWeddingData } = useUserData();
  const [formData, setFormData] = useState({});
  const [saving, setSaving] = useState(false);
  const [sectionEnabled, setSectionEnabled] = useState(true);

  // Auto-save functionality
  useEffect(() => {
    const autoSaveTimeout = setTimeout(() => {
      if (Object.keys(formData).length > 0) {
        autoSave();
      }
    }, 2000); // Auto-save after 2 seconds of inactivity

    return () => clearTimeout(autoSaveTimeout);
  }, [formData]);

  const autoSave = () => {
    if (Object.keys(formData).length > 0) {
      setSaving(true);
      
      // Save form data
      const updatedData = { ...weddingData };
      Object.keys(formData).forEach(field => {
        updatedData[field] = formData[field];
      });
      
      saveWeddingData(updatedData);
      
      setTimeout(() => {
        setSaving(false);
      }, 500);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    
    autoSave();
    
    setTimeout(() => {
      setSaving(false);
      onClose();
    }, 1000);
  };

  const handleChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
  };

  const renderForm = () => {
    switch (sectionId) {
      case 'home':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-semibold" style={{ color: theme.primary }}>
                Edit Home Section
              </h3>
              <div className="flex items-center gap-3">
                <span className="text-sm" style={{ color: theme.textLight }}>Enable Section</span>
                <button
                  onClick={() => setSectionEnabled(!sectionEnabled)}
                  className={`w-12 h-6 rounded-full transition-all duration-300 ${
                    sectionEnabled ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full shadow-md transition-transform duration-300 ${
                    sectionEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: theme.text }}>
                  Bride's Name
                </label>
                <input
                  type="text"
                  defaultValue={weddingData.couple_name_1}
                  onChange={(e) => handleChange('couple_name_1', e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-white/20 border border-white/30 focus:border-opacity-50 transition-all duration-300 backdrop-blur-sm"
                  style={{ color: theme.text, borderColor: `${theme.accent}40` }}
                  placeholder="Enter bride's name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: theme.text }}>
                  Groom's Name
                </label>
                <input
                  type="text"
                  defaultValue={weddingData.couple_name_2}
                  onChange={(e) => handleChange('couple_name_2', e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-white/20 border border-white/30 focus:border-opacity-50 transition-all duration-300 backdrop-blur-sm"
                  style={{ color: theme.text, borderColor: `${theme.accent}40` }}
                  placeholder="Enter groom's name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: theme.text }}>
                  Wedding Date
                </label>
                <input
                  type="date"
                  defaultValue={weddingData.wedding_date}
                  onChange={(e) => handleChange('wedding_date', e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-white/20 border border-white/30 focus:border-opacity-50 transition-all duration-300 backdrop-blur-sm"
                  style={{ color: theme.text, borderColor: `${theme.accent}40` }}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: theme.text }}>
                  Venue Name
                </label>
                <input
                  type="text"
                  defaultValue={weddingData.venue_name}
                  onChange={(e) => handleChange('venue_name', e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-white/20 border border-white/30 focus:border-opacity-50 transition-all duration-300 backdrop-blur-sm"
                  style={{ color: theme.text, borderColor: `${theme.accent}40` }}
                  placeholder="Enter venue name"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: theme.text }}>
                Venue Location
              </label>
              <input
                type="text"
                defaultValue={weddingData.venue_location}
                onChange={(e) => handleChange('venue_location', e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-white/20 border border-white/30 focus:border-opacity-50 transition-all duration-300 backdrop-blur-sm"
                style={{ color: theme.text, borderColor: `${theme.accent}40` }}
                placeholder="Enter full venue address"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: theme.text }}>
                Love Story Description
              </label>
              <textarea
                rows={4}
                defaultValue={weddingData.their_story}
                onChange={(e) => handleChange('their_story', e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-white/20 border border-white/30 focus:border-opacity-50 transition-all duration-300 resize-none backdrop-blur-sm"
                style={{ color: theme.text, borderColor: `${theme.accent}40` }}
                placeholder="Tell your beautiful love story..."
              />
            </div>
          </div>
        );
      
      case 'story':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-semibold" style={{ color: theme.primary }}>
                Edit Our Love Story
              </h3>
              <div className="flex items-center gap-3">
                <span className="text-sm" style={{ color: theme.textLight }}>Enable Section</span>
                <button
                  onClick={() => setSectionEnabled(!sectionEnabled)}
                  className={`w-12 h-6 rounded-full transition-all duration-300 ${
                    sectionEnabled ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full shadow-md transition-transform duration-300 ${
                    sectionEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </div>

            <div className="space-y-4">
              <p className="text-sm" style={{ color: theme.textLight }}>
                Edit each milestone in your love story. You can update the year, title, description, and image for each stage.
              </p>
              
              {weddingData.story_timeline?.map((stage, index) => (
                <div key={index} className="border rounded-xl p-4 bg-white/10" style={{ borderColor: `${theme.accent}30` }}>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2" style={{ color: theme.text }}>
                        Year
                      </label>
                      <input
                        type="text"
                        defaultValue={stage.year}
                        onChange={(e) => {
                          const newTimeline = [...(weddingData.story_timeline || [])];
                          newTimeline[index] = { ...newTimeline[index], year: e.target.value };
                          handleChange('story_timeline', newTimeline);
                        }}
                        className="w-full px-4 py-3 rounded-xl bg-white/20 border border-white/30 focus:border-opacity-50 transition-all duration-300 backdrop-blur-sm"
                        style={{ color: theme.text, borderColor: `${theme.accent}40` }}
                        placeholder="2019"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2" style={{ color: theme.text }}>
                        Title
                      </label>
                      <input
                        type="text"
                        defaultValue={stage.title}
                        onChange={(e) => {
                          const newTimeline = [...(weddingData.story_timeline || [])];
                          newTimeline[index] = { ...newTimeline[index], title: e.target.value };
                          handleChange('story_timeline', newTimeline);
                        }}
                        className="w-full px-4 py-3 rounded-xl bg-white/20 border border-white/30 focus:border-opacity-50 transition-all duration-300 backdrop-blur-sm"
                        style={{ color: theme.text, borderColor: `${theme.accent}40` }}
                        placeholder="First Meeting"
                      />
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <label className="block text-sm font-medium mb-2" style={{ color: theme.text }}>
                      Description
                    </label>
                    <textarea
                      rows={3}
                      defaultValue={stage.description}
                      onChange={(e) => {
                        const newTimeline = [...(weddingData.story_timeline || [])];
                        newTimeline[index] = { ...newTimeline[index], description: e.target.value };
                        handleChange('story_timeline', newTimeline);
                      }}
                      className="w-full px-4 py-3 rounded-xl bg-white/20 border border-white/30 focus:border-opacity-50 transition-all duration-300 resize-none backdrop-blur-sm"
                      style={{ color: theme.text, borderColor: `${theme.accent}40` }}
                      placeholder="Tell the story of this milestone..."
                    />
                  </div>
                  
                  <div className="mt-4">
                    <label className="block text-sm font-medium mb-2" style={{ color: theme.text }}>
                      Image URL
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="url"
                        defaultValue={stage.image}
                        onChange={(e) => {
                          const newTimeline = [...(weddingData.story_timeline || [])];
                          newTimeline[index] = { ...newTimeline[index], image: e.target.value };
                          handleChange('story_timeline', newTimeline);
                        }}
                        className="flex-1 px-4 py-3 rounded-xl bg-white/20 border border-white/30 focus:border-opacity-50 transition-all duration-300 backdrop-blur-sm"
                        style={{ color: theme.text, borderColor: `${theme.accent}40` }}
                        placeholder="https://example.com/image.jpg"
                      />
                      <button
                        type="button"
                        onClick={() => {
                          const newTimeline = [...(weddingData.story_timeline || [])];
                          newTimeline.splice(index, 1);
                          handleChange('story_timeline', newTimeline);
                        }}
                        className="px-4 py-3 rounded-xl bg-red-500/20 border border-red-500/30 hover:bg-red-500/30 transition-all duration-300"
                        style={{ color: '#ef4444' }}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                  
                  {stage.image && (
                    <div className="mt-4">
                      <img 
                        src={stage.image} 
                        alt={stage.title}
                        className="w-full h-32 object-cover rounded-lg"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    </div>
                  )}
                </div>
              ))}
              
              <button
                type="button"
                onClick={() => {
                  const newStage = {
                    year: new Date().getFullYear().toString(),
                    title: "New Milestone",
                    description: "Tell us about this special moment...",
                    image: ""
                  };
                  const newTimeline = [...(weddingData.story_timeline || []), newStage];
                  handleChange('story_timeline', newTimeline);
                }}
                className="w-full py-3 px-4 rounded-xl border-2 border-dashed transition-all duration-300 hover:bg-white/10"
                style={{ 
                  borderColor: `${theme.accent}60`,
                  color: theme.accent
                }}
              >
                + Add New Stage
              </button>
            </div>
          </div>
        );

      case 'schedule':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-semibold" style={{ color: theme.primary }}>
                Edit Wedding Schedule
              </h3>
              <div className="flex items-center gap-3">
                <span className="text-sm" style={{ color: theme.textLight }}>Enable Section</span>
                <button
                  onClick={() => setSectionEnabled(!sectionEnabled)}
                  className={`w-12 h-6 rounded-full transition-all duration-300 ${
                    sectionEnabled ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full shadow-md transition-transform duration-300 ${
                    sectionEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </div>

            <div className="space-y-6">
              {/* Schedule Events */}
              <div>
                <h4 className="text-lg font-semibold mb-4" style={{ color: theme.primary }}>
                  Wedding Day Schedule
                </h4>
                <div className="space-y-4">
                  {weddingData.schedule_events?.map((event, index) => (
                    <div key={index} className="border rounded-xl p-4 bg-white/10" style={{ borderColor: `${theme.accent}30` }}>
                      <div className="grid md:grid-cols-3 gap-4">
                        <div>
                          <label className="block text-sm font-medium mb-2" style={{ color: theme.text }}>
                            Time
                          </label>
                          <input
                            type="text"
                            defaultValue={event.time}
                            onChange={(e) => {
                              const newEvents = [...(weddingData.schedule_events || [])];
                              newEvents[index] = { ...newEvents[index], time: e.target.value };
                              handleChange('schedule_events', newEvents);
                            }}
                            className="w-full px-4 py-3 rounded-xl bg-white/20 border border-white/30 focus:border-opacity-50 transition-all duration-300 backdrop-blur-sm"
                            style={{ color: theme.text, borderColor: `${theme.accent}40` }}
                            placeholder="2:00 PM"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2" style={{ color: theme.text }}>
                            Title
                          </label>
                          <input
                            type="text"
                            defaultValue={event.title}
                            onChange={(e) => {
                              const newEvents = [...(weddingData.schedule_events || [])];
                              newEvents[index] = { ...newEvents[index], title: e.target.value };
                              handleChange('schedule_events', newEvents);
                            }}
                            className="w-full px-4 py-3 rounded-xl bg-white/20 border border-white/30 focus:border-opacity-50 transition-all duration-300 backdrop-blur-sm"
                            style={{ color: theme.text, borderColor: `${theme.accent}40` }}
                            placeholder="Event Title"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2" style={{ color: theme.text }}>
                            Duration
                          </label>
                          <input
                            type="text"
                            defaultValue={event.duration}
                            onChange={(e) => {
                              const newEvents = [...(weddingData.schedule_events || [])];
                              newEvents[index] = { ...newEvents[index], duration: e.target.value };
                              handleChange('schedule_events', newEvents);
                            }}
                            className="w-full px-4 py-3 rounded-xl bg-white/20 border border-white/30 focus:border-opacity-50 transition-all duration-300 backdrop-blur-sm"
                            style={{ color: theme.text, borderColor: `${theme.accent}40` }}
                            placeholder="30 minutes"
                          />
                        </div>
                      </div>
                      
                      <div className="mt-4 grid md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium mb-2" style={{ color: theme.text }}>
                            Description
                          </label>
                          <textarea
                            rows={3}
                            defaultValue={event.description}
                            onChange={(e) => {
                              const newEvents = [...(weddingData.schedule_events || [])];
                              newEvents[index] = { ...newEvents[index], description: e.target.value };
                              handleChange('schedule_events', newEvents);
                            }}
                            className="w-full px-4 py-3 rounded-xl bg-white/20 border border-white/30 focus:border-opacity-50 transition-all duration-300 resize-none backdrop-blur-sm"
                            style={{ color: theme.text, borderColor: `${theme.accent}40` }}
                            placeholder="Event description..."
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2" style={{ color: theme.text }}>
                            Location
                          </label>
                          <input
                            type="text"
                            defaultValue={event.location}
                            onChange={(e) => {
                              const newEvents = [...(weddingData.schedule_events || [])];
                              newEvents[index] = { ...newEvents[index], location: e.target.value };
                              handleChange('schedule_events', newEvents);
                            }}
                            className="w-full px-4 py-3 rounded-xl bg-white/20 border border-white/30 focus:border-opacity-50 transition-all duration-300 backdrop-blur-sm"
                            style={{ color: theme.text, borderColor: `${theme.accent}40` }}
                            placeholder="Event location"
                          />
                          
                          <div className="flex items-center gap-4 mt-3">
                            <label className="flex items-center gap-2 text-sm" style={{ color: theme.text }}>
                              <input
                                type="checkbox"
                                defaultChecked={event.highlight}
                                onChange={(e) => {
                                  const newEvents = [...(weddingData.schedule_events || [])];
                                  newEvents[index] = { ...newEvents[index], highlight: e.target.checked };
                                  handleChange('schedule_events', newEvents);
                                }}
                                className="rounded"
                                style={{ accentColor: theme.accent }}
                              />
                              Highlight this event
                            </label>
                            <button
                              type="button"
                              onClick={() => {
                                const newEvents = [...(weddingData.schedule_events || [])];
                                newEvents.splice(index, 1);
                                handleChange('schedule_events', newEvents);
                              }}
                              className="px-3 py-1 rounded-lg bg-red-500/20 border border-red-500/30 hover:bg-red-500/30 transition-all duration-300 text-sm"
                              style={{ color: '#ef4444' }}
                            >
                              Delete
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  <button
                    type="button"
                    onClick={() => {
                      const newEvent = {
                        time: "12:00 PM",
                        title: "New Event",
                        description: "Event description",
                        location: "Location",
                        icon: "Calendar",
                        duration: "1 hour",
                        highlight: false
                      };
                      const newEvents = [...(weddingData.schedule_events || []), newEvent];
                      handleChange('schedule_events', newEvents);
                    }}
                    className="w-full py-3 px-4 rounded-xl border-2 border-dashed transition-all duration-300 hover:bg-white/10"
                    style={{ 
                      borderColor: `${theme.accent}60`,
                      color: theme.accent
                    }}
                  >
                    + Add New Event
                  </button>
                </div>
              </div>
              
              {/* Important Information Section */}
              <div className="pt-6 border-t border-white/20">
                <h4 className="text-lg font-semibold mb-4" style={{ color: theme.primary }}>
                  Important Information
                </h4>
                <div className="grid md:grid-cols-2 gap-4">
                  {[
                    { id: 'dress_code', label: 'Dress Code', defaultValue: 'Formal/Black Tie Optional. We encourage elegant attire in garden-friendly footwear.' },
                    { id: 'weather_plan', label: 'Weather Plan', defaultValue: 'Our venue has both indoor and covered outdoor spaces for any weather conditions.' },
                    { id: 'transportation', label: 'Transportation', defaultValue: 'Complimentary shuttle service available from nearby hotels. Valet parking provided.' },
                    { id: 'special_accommodations', label: 'Special Accommodations', defaultValue: 'Please let us know of any accessibility needs or dietary restrictions in your RSVP.' }
                  ].map((info) => (
                    <div key={info.id} className="border rounded-xl p-4 bg-white/10" style={{ borderColor: `${theme.accent}30` }}>
                      <div className="flex items-center justify-between mb-3">
                        <label className="text-sm font-medium" style={{ color: theme.text }}>
                          {info.label}
                        </label>
                        <button
                          onClick={() => {
                            const currentInfo = weddingData.important_info || {};
                            const newInfo = { 
                              ...currentInfo, 
                              [info.id]: { 
                                ...currentInfo[info.id], 
                                enabled: !currentInfo[info.id]?.enabled 
                              }
                            };
                            handleChange('important_info', newInfo);
                          }}
                          className={`w-8 h-4 rounded-full transition-all duration-300 ${
                            weddingData.important_info?.[info.id]?.enabled !== false ? 'bg-green-500' : 'bg-gray-300'
                          }`}
                        >
                          <div className={`w-3 h-3 bg-white rounded-full shadow-md transition-transform duration-300 ${
                            weddingData.important_info?.[info.id]?.enabled !== false ? 'translate-x-4' : 'translate-x-0.5'
                          }`} />
                        </button>
                      </div>
                      <textarea
                        rows={3}
                        defaultValue={weddingData.important_info?.[info.id]?.text || info.defaultValue}
                        onChange={(e) => {
                          const currentInfo = weddingData.important_info || {};
                          const newInfo = { 
                            ...currentInfo, 
                            [info.id]: { 
                              ...currentInfo[info.id], 
                              text: e.target.value 
                            }
                          };
                          handleChange('important_info', newInfo);
                        }}
                        className="w-full px-4 py-3 rounded-xl bg-white/20 border border-white/30 focus:border-opacity-50 transition-all duration-300 resize-none backdrop-blur-sm text-sm"
                        style={{ color: theme.text, borderColor: `${theme.accent}40` }}
                        placeholder={info.defaultValue}
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );

      case 'rsvp':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-semibold" style={{ color: theme.primary }}>
                Edit RSVP Section
              </h3>
              <div className="flex items-center gap-3">
                <span className="text-sm" style={{ color: theme.textLight }}>Enable Section</span>
                <button
                  onClick={() => setSectionEnabled(!sectionEnabled)}
                  className={`w-12 h-6 rounded-full transition-all duration-300 ${
                    sectionEnabled ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full shadow-md transition-transform duration-300 ${
                    sectionEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </div>
            
            <div className="text-center py-12">
              <div 
                className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                style={{ background: theme.gradientAccent }}
              >
                <Mail className="w-8 h-8" style={{ color: theme.primary }} />
              </div>
              <p className="text-lg mb-2" style={{ color: theme.text }}>
                RSVP Form Configuration
              </p>
              <p className="text-sm" style={{ color: theme.textLight }}>
                RSVP form settings and response management will be available here. This includes form fields, deadline settings, and guest response tracking.
              </p>
            </div>
          </div>
        );

      case 'gallery':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-semibold" style={{ color: theme.primary }}>
                Edit Photo Gallery
              </h3>
              <div className="flex items-center gap-3">
                <span className="text-sm" style={{ color: theme.textLight }}>Enable Section</span>
                <button
                  onClick={() => setSectionEnabled(!sectionEnabled)}
                  className={`w-12 h-6 rounded-full transition-all duration-300 ${
                    sectionEnabled ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full shadow-md transition-transform duration-300 ${
                    sectionEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </div>
            
            <div className="text-center py-12">
              <div 
                className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                style={{ background: theme.gradientAccent }}
              >
                <Image className="w-8 h-8" style={{ color: theme.primary }} />
              </div>
              <p className="text-lg mb-2" style={{ color: theme.text }}>
                Photo Gallery Management
              </p>
              <p className="text-sm" style={{ color: theme.textLight }}>
                Upload and organize your engagement photos, couple photos, and other memories to be displayed in the gallery section.
              </p>
            </div>
          </div>
        );

      case 'party':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-semibold" style={{ color: theme.primary }}>
                Edit Wedding Party
              </h3>
              <div className="flex items-center gap-3">
                <span className="text-sm" style={{ color: theme.textLight }}>Enable Section</span>
                <button
                  onClick={() => setSectionEnabled(!sectionEnabled)}
                  className={`w-12 h-6 rounded-full transition-all duration-300 ${
                    sectionEnabled ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full shadow-md transition-transform duration-300 ${
                    sectionEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </div>
            
            <div className="text-center py-12">
              <div 
                className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                style={{ background: theme.gradientAccent }}
              >
                <Users className="w-8 h-8" style={{ color: theme.primary }} />
              </div>
              <p className="text-lg mb-2" style={{ color: theme.text }}>
                Wedding Party Management
              </p>
              <p className="text-sm" style={{ color: theme.textLight }}>
                Add and edit information about your bridal party and groomsmen, including photos, names, roles, and relationships.
              </p>
            </div>
          </div>
        );

      case 'registry':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-semibold" style={{ color: theme.primary }}>
                Edit Gift Registry
              </h3>
              <div className="flex items-center gap-3">
                <span className="text-sm" style={{ color: theme.textLight }}>Enable Section</span>
                <button
                  onClick={() => setSectionEnabled(!sectionEnabled)}
                  className={`w-12 h-6 rounded-full transition-all duration-300 ${
                    sectionEnabled ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full shadow-md transition-transform duration-300 ${
                    sectionEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </div>
            
            <div className="text-center py-12">
              <div 
                className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                style={{ background: theme.gradientAccent }}
              >
                <Gift className="w-8 h-8" style={{ color: theme.primary }} />
              </div>
              <p className="text-lg mb-2" style={{ color: theme.text }}>
                Gift Registry Links
              </p>
              <p className="text-sm" style={{ color: theme.textLight }}>
                Add links to your wedding registries from different stores and your honeymoon fund information.
              </p>
            </div>
          </div>
        );

      case 'guestbook':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-semibold" style={{ color: theme.primary }}>
                Edit Guest Book
              </h3>
              <div className="flex items-center gap-3">
                <span className="text-sm" style={{ color: theme.textLight }}>Enable Section</span>
                <button
                  onClick={() => setSectionEnabled(!sectionEnabled)}
                  className={`w-12 h-6 rounded-full transition-all duration-300 ${
                    sectionEnabled ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full shadow-md transition-transform duration-300 ${
                    sectionEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </div>
            
            <div className="text-center py-12">
              <div 
                className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                style={{ background: theme.gradientAccent }}
              >
                <MessageCircle className="w-8 h-8" style={{ color: theme.primary }} />
              </div>
              <p className="text-lg mb-2" style={{ color: theme.text }}>
                Guest Book Messages
              </p>
              <p className="text-sm" style={{ color: theme.textLight }}>
                Configure the guest book section where friends and family can leave heartfelt messages and well wishes.
              </p>
            </div>
          </div>
        );

      case 'faq':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-semibold" style={{ color: theme.primary }}>
                Edit FAQ Section
              </h3>
              <div className="flex items-center gap-3">
                <span className="text-sm" style={{ color: theme.textLight }}>Enable Section</span>
                <button
                  onClick={() => setSectionEnabled(!sectionEnabled)}
                  className={`w-12 h-6 rounded-full transition-all duration-300 ${
                    sectionEnabled ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full shadow-md transition-transform duration-300 ${
                    sectionEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </div>
            
            <div className="text-center py-12">
              <div 
                className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                style={{ background: theme.gradientAccent }}
              >
                <HelpCircle className="w-8 h-8" style={{ color: theme.primary }} />
              </div>
              <p className="text-lg mb-2" style={{ color: theme.text }}>
                Frequently Asked Questions
              </p>
              <p className="text-sm" style={{ color: theme.textLight }}>
                Add and edit common questions and answers about your wedding to help guests prepare for your special day.
              </p>
            </div>
          </div>
        );

      case 'theme':
        return (
          <div className="space-y-6">
            <h3 className="text-2xl font-semibold mb-6" style={{ color: theme.primary }}>
              Choose Your Theme
            </h3>
            <div className="grid grid-cols-3 gap-4">
              {['classic', 'modern', 'boho'].map((themeName) => (
                <button
                  key={themeName}
                  onClick={() => handleChange('theme', themeName)}
                  className={`p-6 rounded-2xl border-2 transition-all duration-300 hover:scale-105 ${
                    weddingData.theme === themeName ? 'border-current' : 'border-transparent'
                  }`}
                  style={{ 
                    background: 'rgba(255,255,255,0.1)',
                    borderColor: weddingData.theme === themeName ? theme.accent : 'transparent'
                  }}
                >
                  <div className="text-lg font-semibold capitalize mb-2" style={{ color: theme.primary }}>
                    {themeName === 'classic' && '🎭'} {themeName === 'modern' && '🚀'} {themeName === 'boho' && '🌸'} {themeName}
                  </div>
                  <div className="text-sm" style={{ color: theme.textLight }}>
                    {themeName === 'classic' && 'Elegant and timeless'}
                    {themeName === 'modern' && 'Clean and contemporary'}
                    {themeName === 'boho' && 'Bohemian and romantic'}
                  </div>
                </button>
              ))}
            </div>
          </div>
        );

      case 'ai-design':
        return (
          <div className="space-y-6">
            <h3 className="text-2xl font-semibold mb-6" style={{ color: theme.primary }}>
              AI Design Generator
            </h3>
            <div className="text-center py-12">
              <div 
                className="w-20 h-20 mx-auto mb-6 rounded-full flex items-center justify-center animate-pulse"
                style={{ background: theme.gradientAccent }}
              >
                <Wand2 className="w-10 h-10" style={{ color: theme.primary }} />
              </div>
              <p className="text-lg mb-4" style={{ color: theme.text }}>
                AI-Powered Design Coming Soon!
              </p>
              <p className="text-sm mb-6" style={{ color: theme.textLight }}>
                Our AI will generate beautiful, personalized wedding card designs based on your preferences, theme, and story.
              </p>
              <div className="bg-gradient-to-r from-purple-100 to-pink-100 rounded-2xl p-6 text-left">
                <h4 className="font-semibold mb-3 text-purple-800">Features will include:</h4>
                <ul className="space-y-2 text-sm text-purple-700">
                  <li>• Color scheme suggestions based on your theme</li>
                  <li>• Layout optimization for your content</li>
                  <li>• Font pairing recommendations</li>
                  <li>• Background pattern generation</li>
                  <li>• Multiple design variations to choose from</li>
                </ul>
              </div>
            </div>
          </div>
        );

      case 'custom-url':
        return <CustomUrlForm theme={theme} weddingData={weddingData} saveWeddingData={saveWeddingData} />;

      case 'qrcode-generator':
        return <QRCodeGeneratorForm theme={theme} weddingData={weddingData} />;

      default:
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-semibold" style={{ color: theme.primary }}>
                Edit {sectionId.charAt(0).toUpperCase() + sectionId.slice(1)} Section
              </h3>
              <div className="flex items-center gap-3">
                <span className="text-sm" style={{ color: theme.textLight }}>Enable Section</span>
                <button
                  onClick={() => setSectionEnabled(!sectionEnabled)}
                  className={`w-12 h-6 rounded-full transition-all duration-300 ${
                    sectionEnabled ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full shadow-md transition-transform duration-300 ${
                    sectionEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </div>
            
            <div className="text-center py-12">
              <div 
                className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                style={{ background: theme.gradientAccent }}
              >
                <Plus className="w-8 h-8" style={{ color: theme.primary }} />
              </div>
              <p className="text-lg mb-2" style={{ color: theme.text }}>
                Enhanced form for {sectionId} section
              </p>
              <p className="text-sm" style={{ color: theme.textLight }}>
                This section will contain pre-populated data from your landing page. You can edit, replace, or remove any content here.
              </p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[50] flex items-center justify-center p-4">
      <div 
        ref={modalRef}
        className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border"
        style={{ 
          border: `1px solid ${theme.accent}30`,
          background: `linear-gradient(135deg, ${theme.background}f8, ${theme.secondary}f0)`
        }}
      >
        <div className="p-8">
          {/* Header with auto-save indicator */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              {saving && (
                <div className="flex items-center gap-2 text-green-600">
                  <div className="w-4 h-4 border-2 border-green-600 border-t-transparent rounded-full animate-spin"></div>
                  <span className="text-sm">Auto-saving...</span>
                </div>
              )}
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-full hover:bg-black/10 transition-colors duration-200"
              style={{ color: theme.textLight }}
            >
              <X className="w-6 h-6" />
            </button>
          </div>
          
          <form onSubmit={handleSubmit}>
            {renderForm()}
            
            <div className="flex justify-between items-center mt-8">
              <div className="text-sm opacity-70" style={{ color: theme.textLight }}>
                💡 Click outside or press ESC to auto-save and close
              </div>
              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-6 py-3 rounded-xl border border-gray-300 hover:bg-gray-50 transition-colors duration-200"
                  style={{ color: theme.text }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-6 py-3 rounded-xl font-semibold transition-all duration-300 hover:scale-105 disabled:opacity-50"
                  style={{
                    background: theme.gradientAccent,
                    color: theme.primary
                  }}
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// Custom URL Form Component
const CustomUrlForm = ({ theme, weddingData, saveWeddingData }) => {
  const { userInfo } = useUserData();
  const [customUrl, setCustomUrl] = useState(weddingData.custom_url || '');
  const [previewUrl, setPreviewUrl] = useState('');
  const [isCopied, setIsCopied] = useState(false);

  useEffect(() => {
    if (customUrl) {
      setPreviewUrl(`${window.location.origin}/${customUrl}`);
    } else {
      setPreviewUrl(`${window.location.origin}/wedding/${userInfo.userId}`);
    }
  }, [customUrl, userInfo.userId]);

  const handleSaveUrl = () => {
    const updatedData = { ...weddingData, custom_url: customUrl };
    saveWeddingData(updatedData);
  };

  const handleCopyUrl = () => {
    copyToClipboardWithFallback(previewUrl).then(() => {
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    }).catch((error) => {
      console.error('Failed to copy URL:', error);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    });
  };

  const generateSuggestions = () => {
    const name1 = weddingData.couple_name_1?.toLowerCase().replace(/\s+/g, '') || 'bride';
    const name2 = weddingData.couple_name_2?.toLowerCase().replace(/\s+/g, '') || 'groom';
    return [
      `${name1}-${name2}-wedding`,
      `${name1}and${name2}`,
      `${name1}-${name2}-2025`,
      `wedding-${name1}-${name2}`,
      `${name1}${name2}wedding`
    ];
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-2xl font-semibold" style={{ color: theme.primary }}>
          Customize Your Wedding URL
        </h3>
        <div className="flex items-center gap-2">
          <Link className="w-6 h-6" style={{ color: theme.accent }} />
        </div>
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6">
        <h4 className="font-semibold mb-3 text-blue-800">Create Your Perfect Wedding URL</h4>
        <p className="text-sm text-blue-700 mb-4">
          Make your wedding card easy to remember and share with a custom URL that reflects your love story.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2" style={{ color: theme.text }}>
            Custom URL Route
          </label>
          <div className="flex items-center gap-2">
            <span className="text-sm px-3 py-3 bg-gray-100 rounded-l-xl border-r-0" style={{ color: theme.textLight }}>
              {window.location.origin}/
            </span>
            <input
              type="text"
              value={customUrl}
              onChange={(e) => {
                const value = e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '');
                setCustomUrl(value);
              }}
              className="flex-1 px-4 py-3 rounded-r-xl bg-white/20 border border-white/30 focus:border-opacity-50 transition-all duration-300 backdrop-blur-sm"
              style={{ color: theme.text, borderColor: `${theme.accent}40` }}
              placeholder="sarah-michael-wedding"
            />
          </div>
          <p className="text-xs mt-1" style={{ color: theme.textLight }}>
            Only lowercase letters, numbers, and hyphens allowed
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2" style={{ color: theme.text }}>
            Preview URL
          </label>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={previewUrl}
              readOnly
              className="flex-1 px-4 py-3 rounded-xl bg-gray-100 border border-gray-200"
              style={{ color: theme.text }}
            />
            <button
              onClick={handleCopyUrl}
              className="px-4 py-3 rounded-xl transition-all duration-300 hover:scale-105"
              style={{
                background: isCopied ? '#10b981' : theme.gradientAccent,
                color: theme.primary
              }}
            >
              {isCopied ? <CheckCircle className="w-5 h-5" /> : <Copy className="w-5 h-5" />}
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-3" style={{ color: theme.text }}>
            URL Suggestions
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {generateSuggestions().map((suggestion, index) => (
              <button
                key={index}
                onClick={() => setCustomUrl(suggestion)}
                className="text-left px-3 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition-all duration-200 text-sm"
                style={{ color: theme.textLight }}
              >
                {window.location.origin}/{suggestion}
              </button>
            ))}
          </div>
        </div>

        <div className="flex justify-end">
          <button
            onClick={handleSaveUrl}
            className="px-6 py-3 rounded-xl font-semibold transition-all duration-300 hover:scale-105"
            style={{
              background: theme.gradientAccent,
              color: theme.primary
            }}
          >
            Save Custom URL
          </button>
        </div>
      </div>
    </div>
  );
};

// QR Code Generator Form Component
const QRCodeGeneratorForm = ({ theme, weddingData }) => {
  const { userInfo } = useUserData();
  const [selectedFormat, setSelectedFormat] = useState('300x300');
  const [selectedStyle, setSelectedStyle] = useState('default');
  const [qrUrl, setQrUrl] = useState('');

  const formats = [
    { id: '200x200', label: 'Small (200x200)', size: '200x200' },
    { id: '300x300', label: 'Medium (300x300)', size: '300x300' },
    { id: '500x500', label: 'Large (500x500)', size: '500x500' },
    { id: '800x800', label: 'Extra Large (800x800)', size: '800x800' }
  ];

  const styles = [
    { id: 'default', label: 'Classic Black', color: '000000', bgcolor: 'ffffff' },
    { id: 'gold', label: 'Elegant Gold', color: 'd4af37', bgcolor: 'ffffff' },
    { id: 'modern', label: 'Modern Blue', color: '3b82f6', bgcolor: 'ffffff' },
    { id: 'romantic', label: 'Romantic Pink', color: 'ec4899', bgcolor: 'ffffff' }
  ];

  useEffect(() => {
    const weddingUrl = weddingData.custom_url 
      ? `${window.location.origin}/${weddingData.custom_url}`
      : `${window.location.origin}/wedding/${userInfo.userId}`;
    
    const selectedStyleObj = styles.find(s => s.id === selectedStyle);
    const qrApiUrl = `https://api.qrserver.com/v1/create-qr-code/?size=${selectedFormat}&data=${encodeURIComponent(weddingUrl)}&color=${selectedStyleObj.color}&bgcolor=${selectedStyleObj.bgcolor}`;
    setQrUrl(qrApiUrl);
  }, [selectedFormat, selectedStyle, weddingData.custom_url, userInfo.userId]);

  const handleDownload = (format) => {
    const link = document.createElement('a');
    link.href = qrUrl.replace(selectedFormat, format);
    link.download = `wedding-qr-code-${format}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handlePrint = () => {
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
        <head>
          <title>Wedding QR Code - ${weddingData.couple_name_1} & ${weddingData.couple_name_2}</title>
          <style>
            body { 
              display: flex; 
              flex-direction: column; 
              align-items: center; 
              justify-content: center; 
              min-height: 100vh; 
              font-family: Arial, sans-serif; 
              background: linear-gradient(135deg, #f8f6f0, #ffffff);
              margin: 0;
              padding: 20px;
            }
            .header { text-align: center; margin-bottom: 30px; }
            .qr-container { text-align: center; }
            .qr-code { border: 4px solid #${styles.find(s => s.id === selectedStyle).color}; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            .couple-names { font-size: 24px; color: #333; margin-bottom: 10px; font-weight: bold; }
            .date { font-size: 18px; color: #666; margin-bottom: 20px; }
            .instruction { color: #666; margin-top: 20px; font-size: 14px; }
          </style>
        </head>
        <body>
          <div class="header">
            <div class="couple-names">${weddingData.couple_name_1} & ${weddingData.couple_name_2}</div>
            <div class="date">${weddingData.wedding_date}</div>
          </div>
          <div class="qr-container">
            <img src="${qrUrl}" alt="Wedding QR Code" class="qr-code" />
            <p class="instruction">Scan this QR code to view our wedding invitation</p>
          </div>
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-2xl font-semibold" style={{ color: theme.primary }}>
          Generate QR Code
        </h3>
        <div className="flex items-center gap-2">
          <QrCode className="w-6 h-6" style={{ color: theme.accent }} />
        </div>
      </div>

      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl p-6">
        <h4 className="font-semibold mb-3 text-purple-800">Beautiful QR Codes for Your Wedding</h4>
        <p className="text-sm text-purple-700">
          Generate stylish QR codes in different sizes and colors that guests can scan to view your wedding invitation.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-3" style={{ color: theme.text }}>
              QR Code Size
            </label>
            <div className="space-y-2">
              {formats.map((format) => (
                <button
                  key={format.id}
                  onClick={() => setSelectedFormat(format.size)}
                  className={`w-full text-left px-4 py-3 rounded-xl transition-all duration-300 ${
                    selectedFormat === format.size ? 'shadow-lg' : 'hover:shadow-md'
                  }`}
                  style={{
                    background: selectedFormat === format.size 
                      ? theme.gradientAccent 
                      : 'rgba(255,255,255,0.1)',
                    color: selectedFormat === format.size 
                      ? theme.primary 
                      : theme.text
                  }}
                >
                  {format.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-3" style={{ color: theme.text }}>
              QR Code Style
            </label>
            <div className="space-y-2">
              {styles.map((style) => (
                <button
                  key={style.id}
                  onClick={() => setSelectedStyle(style.id)}
                  className={`w-full text-left px-4 py-3 rounded-xl transition-all duration-300 flex items-center gap-3 ${
                    selectedStyle === style.id ? 'shadow-lg' : 'hover:shadow-md'
                  }`}
                  style={{
                    background: selectedStyle === style.id 
                      ? theme.gradientAccent 
                      : 'rgba(255,255,255,0.1)',
                    color: selectedStyle === style.id 
                      ? theme.primary 
                      : theme.text
                  }}
                >
                  <div 
                    className="w-4 h-4 rounded-full border-2"
                    style={{ backgroundColor: `#${style.color}`, borderColor: `#${style.bgcolor}` }}
                  />
                  {style.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-3" style={{ color: theme.text }}>
              Preview
            </label>
            <div className="bg-white rounded-2xl p-6 text-center shadow-lg">
              {qrUrl && (
                <img 
                  src={qrUrl} 
                  alt="QR Code Preview" 
                  className="mx-auto rounded-lg shadow-md"
                  style={{ maxWidth: '200px', height: 'auto' }}
                />
              )}
              <p className="text-sm text-gray-600 mt-4">
                {weddingData.couple_name_1} & {weddingData.couple_name_2}
              </p>
              <p className="text-xs text-gray-500">
                Scan to view wedding invitation
              </p>
            </div>
          </div>

          <div className="space-y-2">
            <button
              onClick={() => handleDownload(selectedFormat)}
              className="w-full px-4 py-3 rounded-xl font-medium transition-all duration-300 hover:scale-105 flex items-center justify-center gap-2"
              style={{
                background: theme.gradientAccent,
                color: theme.primary
              }}
            >
              <Download className="w-4 h-4" />
              Download QR Code
            </button>

            <button
              onClick={handlePrint}
              className="w-full px-4 py-3 rounded-xl border border-gray-300 hover:bg-gray-50 transition-all duration-300 flex items-center justify-center gap-2"
              style={{ color: theme.text }}
            >
              📄 Print QR Code
            </button>

            <div className="text-center">
              <p className="text-xs" style={{ color: theme.textLight }}>
                Download multiple sizes:
              </p>
              <div className="flex gap-2 mt-2">
                {formats.map((format) => (
                  <button
                    key={format.id}
                    onClick={() => handleDownload(format.size)}
                    className="text-xs px-3 py-1 rounded-full bg-white/20 hover:bg-white/30 transition-all duration-200"
                    style={{ color: theme.textLight }}
                  >
                    {format.size}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeftSidebar;