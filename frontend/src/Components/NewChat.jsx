import React, { useState, useEffect, useRef } from 'react';
import { Avatar, Box, Text, VStack, HStack, Button, Input, Table, Thead, Tbody, Tr, Th, Td } from '@chakra-ui/react';
import { BeatLoader } from 'react-spinners';

const Chat = () => {
    const [messages, setMessages] = useState([]);
    const [userInput, setUserInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [courseList, setCourseList] = useState([]);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async () => {
        if (!userInput.trim()) return;
    
        setMessages(prevMessages => [
            ...prevMessages, 
            { type: 'user', text: userInput }
        ]);
        setIsLoading(true);
    
        try {
            const response = await fetch('http://localhost:5000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userInput }),
            });
    
            const data = await response.json();
    
            if (data.error) {
                setMessages(prevMessages => [
                    ...prevMessages, 
                    { type: 'error', text: data.error }
                ]);
            } else {
                // the agent response to the chat
                setMessages(prevMessages => [
                    ...prevMessages, 
                    { type: 'agent', text: data.message }
                ]);
    
                // Optionally handle courses and faculty lists
                if (data.faculty.length > 0) {
                    // Convert faculty list to table format
                    const facultyTable = (
                        <table>
                            <thead>
                                <tr>
                                    <th>Faculty Name</th>
                                    
                                    <th>Gender</th>
                                    &nbsp;
                                    &nbsp;
                                    <th>Department</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.faculty.map((faculty, index) => (
                                    <tr key={index}>
                                        <td>{faculty.name}</td>
                                        <td>{faculty.gender === 'Male' ? 'Male' : 'Female'}</td>
                                        &nbsp;
                                        &nbsp;
                                        &nbsp;
                                        <td>{faculty.department}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    );
    
                    // Add the table to the chat
                    setMessages(prevMessages => [
                        ...prevMessages, 
                        { type: 'agent', text: facultyTable }
                    ]);
                }
            }
        } catch (error) {
            setMessages(prevMessages => [
                ...prevMessages, 
                { type: 'error', text: 'Server error. Try again later.' }
            ]);
        } finally {
            setIsLoading(false);
            setUserInput('');
        }
    };    
    
    useEffect(() => {
        console.log("Current messages:", messages);
    }, [messages]);

    return (
        <Box
            flex="1"
            p="4"
            bg="white"
            overflowY="auto"
            width="80%"
            marginTop="15rem"
            border="1px solid"
            borderColor="gray.200"
            height="600px"
            display="flex"
            flexDirection="column"
        >
            <VStack spacing="4" align="stretch" flex="1" overflowY="auto">
                {messages.map((msg, index) => (
                    <HStack
                        key={index}
                        spacing="4"
                        align="start"
                        alignSelf={msg.type === 'user' ? 'flex-end' : 'flex-start'}
                    >
                        {msg.type === 'agent' && (
                            <Avatar
                                name="Bot"
                                size="xs"
                                bg="gray.200"
                                mt={5}
                            />
                        )}
                        <Box p="2" bg={msg.type === 'user' ? 'blue.100' : 'gray.100'} borderRadius="10">
                            <Text>{msg.text}</Text>
                        </Box>
                        {msg.type === 'user' && (
                            <Avatar
                                name="User"
                                size="xs"
                                bg="blue.200"
                                mt={5}
                            />
                        )}
                    </HStack>
                ))}
                <div ref={messagesEndRef} />
            </VStack>

            <HStack spacing="4" mt="4">
                <Input
                    id="chat-input"
                    name="chat-input"
                    flex="1"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Type your message..."
                />
                <Button colorScheme="blue" onClick={sendMessage} isDisabled={isLoading}>
                    {isLoading ? <BeatLoader size={8} color="white" /> : 'Send'}
                </Button>
            </HStack>
        </Box>
    );
};

export default Chat;