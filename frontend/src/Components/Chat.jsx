import React, {useEffect, useRef } from 'react';
import { Avatar, Box, Text, VStack, HStack} from '@chakra-ui/react';

const Chat = ({messages}) => {
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);    
    
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
            marginTop="6rem"
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
        </Box>
    );
};

export default Chat;